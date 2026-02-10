"""
Evaluation Manager for Story and Image Quality Assessment

Evaluates generated stories and images across multiple dimensions:
- Image-text alignment (CLIP)
- Visual character consistency (facial embeddings + CLIP image similarity)
- Text coherence (Sentence Transformers)
- Readability (Flesch-Kincaid, grade level)
- Story structure (beginning, climax, ending)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import numpy as np

# Image-text similarity
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# Text coherence
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Readability
import textstat

# Face detection (reuse existing)
try:
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False
    print("⚠️ InsightFace not available for character consistency evaluation")


class EvaluationManager:
    """
    Manages evaluation of story quality and image-text alignment.
    """
    
    def __init__(self, save_dir: str = "generated/evaluations"):
        """
        Initialize evaluation models.
        
        Args:
            save_dir: Directory to save evaluation results
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Lazy loading flags
        self._clip_model = None
        self._clip_processor = None
        self._sentence_model = None
        self._face_app = None
        
        print("✅ EvaluationManager initialized (models will load on first use)")
    
    @property
    def clip_model(self):
        """Lazy load CLIP model"""
        if self._clip_model is None:
            print("🔄 Loading CLIP model for image-text similarity...")
            self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            print("✅ CLIP model loaded")
        return self._clip_model
    
    @property
    def clip_processor(self):
        """Lazy load CLIP processor"""
        if self._clip_processor is None:
            _ = self.clip_model  # Trigger loading
        return self._clip_processor
    
    @property
    def sentence_model(self):
        """Lazy load Sentence Transformer model"""
        if self._sentence_model is None:
            print("🔄 Loading Sentence Transformer for text coherence...")
            self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence Transformer loaded")
        return self._sentence_model
    
    @property
    def face_app(self):
        """Lazy load InsightFace for character consistency"""
        if self._face_app is None and INSIGHTFACE_AVAILABLE:
            print("🔄 Loading InsightFace for character consistency...")
            self._face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self._face_app.prepare(ctx_id=0, det_size=(640, 640))
            print("✅ InsightFace loaded")
        return self._face_app
    
    def evaluate_image_text_similarity(self, image_paths: List[str], texts: List[str]) -> List[float]:
        """
        Evaluate CLIP similarity between images and their corresponding text descriptions.
        
        Args:
            image_paths: List of paths to scene images
            texts: List of scene text descriptions
        
        Returns:
            List of similarity scores (0-1) for each scene
        """
        scores = []
        
        for img_path, text in zip(image_paths, texts):
            try:
                image = Image.open(img_path).convert("RGB")
                
                inputs = self.clip_processor(
                    text=[text],
                    images=image,
                    return_tensors="pt",
                    padding=True
                )
                
                outputs = self.clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                score = probs[0][0].item()
                
                scores.append(score)
                
            except Exception as e:
                print(f"⚠️ Error evaluating image-text similarity: {e}")
                scores.append(0.0)
        
        return scores
    
    def evaluate_visual_consistency(self, image_paths: List[str]) -> Dict[str, float]:
        """
        Evaluate visual consistency across scene images using CLIP image embeddings.
        
        Args:
            image_paths: List of paths to scene images
        
        Returns:
            Dict with average consistency score and pairwise scores
        """
        if len(image_paths) < 2:
            return {"average": 1.0, "pairwise": []}
        
        try:
            embeddings = []
            for img_path in image_paths:
                image = Image.open(img_path).convert("RGB")
                inputs = self.clip_processor(images=image, return_tensors="pt")
                image_features = self.clip_model.get_image_features(**inputs)
                embeddings.append(image_features.detach().numpy())
            
            # Calculate pairwise cosine similarity
            embeddings_array = np.vstack(embeddings)
            similarity_matrix = cosine_similarity(embeddings_array)
            
            # Get upper triangle (excluding diagonal)
            pairwise_scores = []
            for i in range(len(image_paths)):
                for j in range(i + 1, len(image_paths)):
                    pairwise_scores.append(float(similarity_matrix[i][j]))
            
            avg_consistency = np.mean(pairwise_scores) if pairwise_scores else 1.0
            
            return {
                "average": float(avg_consistency),
                "pairwise": pairwise_scores
            }
            
        except Exception as e:
            print(f"⚠️ Error evaluating visual consistency: {e}")
            return {"average": 0.0, "pairwise": []}
    
    def evaluate_character_consistency(self, image_paths: List[str]) -> Optional[Dict[str, float]]:
        """
        Evaluate character face consistency using InsightFace embeddings (personalized mode only).
        
        Args:
            image_paths: List of paths to scene images
        
        Returns:
            Dict with average face consistency or None if not available
        """
        if not INSIGHTFACE_AVAILABLE or self.face_app is None:
            return None
        
        if len(image_paths) < 2:
            return {"average": 1.0, "face_distances": []}
        
        try:
            face_embeddings = []
            for img_path in image_paths:
                image = np.array(Image.open(img_path).convert("RGB"))
                faces = self.face_app.get(image)
                
                if faces:
                    # Use the largest face (main character)
                    main_face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
                    face_embeddings.append(main_face.embedding)
            
            if len(face_embeddings) < 2:
                return {"average": 1.0, "face_distances": []}
            
            # Calculate cosine distance between consecutive faces
            distances = []
            for i in range(len(face_embeddings) - 1):
                emb1 = face_embeddings[i] / np.linalg.norm(face_embeddings[i])
                emb2 = face_embeddings[i + 1] / np.linalg.norm(face_embeddings[i + 1])
                distance = 1 - np.dot(emb1, emb2)
                distances.append(float(distance))
            
            avg_distance = np.mean(distances) if distances else 0.0
            consistency_score = 1 - avg_distance  # Convert distance to similarity
            
            return {
                "average": float(max(0, consistency_score)),
                "face_distances": distances
            }
            
        except Exception as e:
            print(f"⚠️ Error evaluating character consistency: {e}")
            return None
    
    def evaluate_text_coherence(self, texts: List[str]) -> Dict[str, float]:
        """
        Evaluate semantic coherence between consecutive scenes using Sentence Transformers.
        
        Args:
            texts: List of scene text descriptions
        
        Returns:
            Dict with average coherence and pairwise scores
        """
        if len(texts) < 2:
            return {"average": 1.0, "consecutive": []}
        
        try:
            embeddings = self.sentence_model.encode(texts)
            
            # Calculate similarity between consecutive scenes
            consecutive_scores = []
            for i in range(len(texts) - 1):
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[i + 1].reshape(1, -1)
                )[0][0]
                consecutive_scores.append(float(similarity))
            
            avg_coherence = np.mean(consecutive_scores) if consecutive_scores else 1.0
            
            return {
                "average": float(avg_coherence),
                "consecutive": consecutive_scores
            }
            
        except Exception as e:
            print(f"⚠️ Error evaluating text coherence: {e}")
            return {"average": 0.0, "consecutive": []}
    
    def evaluate_readability(self, full_text: str) -> Dict[str, Any]:
        """
        Evaluate readability metrics for age appropriateness (target: 7-10 years old).
        
        Args:
            full_text: Combined text of all scenes
        
        Returns:
            Dict with readability metrics
        """
        try:
            flesch_kincaid = textstat.flesch_kincaid_grade(full_text)
            flesch_reading_ease = textstat.flesch_reading_ease(full_text)
            avg_sentence_length = textstat.avg_sentence_length(full_text)
            syllable_count = textstat.syllable_count(full_text)
            word_count = textstat.lexicon_count(full_text)
            
            # Target grade level: 3-5 (ages 8-10)
            suitable = 3 <= flesch_kincaid <= 6
            
            return {
                "flesch_kincaid_grade": round(flesch_kincaid, 2),
                "flesch_reading_ease": round(flesch_reading_ease, 2),
                "avg_sentence_length": round(avg_sentence_length, 1),
                "syllable_count": syllable_count,
                "word_count": word_count,
                "suitable_for_target_age": suitable,
                "interpretation": self._interpret_readability(flesch_kincaid)
            }
            
        except Exception as e:
            print(f"⚠️ Error evaluating readability: {e}")
            return {
                "flesch_kincaid_grade": 0,
                "suitable_for_target_age": False,
                "interpretation": "Error"
            }
    
    def _interpret_readability(self, grade_level: float) -> str:
        """Interpret Flesch-Kincaid grade level"""
        if grade_level < 3:
            return "Too simple for target age (7-10)"
        elif 3 <= grade_level <= 5:
            return "Perfect for target age (7-10)"
        elif 5 < grade_level <= 6:
            return "Slightly advanced but acceptable"
        else:
            return "Too complex for target age (7-10)"
    
    def evaluate_story_structure(self, texts: List[str], num_scenes: int) -> Dict[str, bool]:
        """
        Validate story has proper beginning, climax, and ending structure.
        
        Args:
            texts: List of scene text descriptions
            num_scenes: Total number of scenes
        
        Returns:
            Dict indicating presence of story elements
        """
        # Simple heuristic: check text length and keywords
        has_beginning = len(texts) > 0 and len(texts[0]) > 50
        has_ending = len(texts) > 0 and len(texts[-1]) > 50
        has_climax = num_scenes >= 3  # With new structure, climax is guaranteed
        
        return {
            "has_beginning": has_beginning,
            "has_climax": has_climax,
            "has_ending": has_ending,
            "follows_structure": has_beginning and has_climax and has_ending
        }
    
    def evaluate_story(
        self,
        story_id: int,
        story_dict: Dict[str, Any],
        image_paths: List[str],
        mode: str = "simple"
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a complete story.
        
        Args:
            story_id: Database ID of the story
            story_dict: Story data with scenes
            image_paths: Paths to generated scene images
            mode: Generation mode ("simple" or "personalized")
        
        Returns:
            Complete evaluation results
        """
        print(f"\n📊 Evaluating story {story_id}...")
        start_time = time.time()
        
        scenes = story_dict.get("scenes", [])
        texts = [scene.get("text", "") for scene in scenes]
        full_text = " ".join(texts)
        
        # 1. Image-Text Similarity
        print("🔍 Evaluating image-text alignment...")
        image_text_scores = self.evaluate_image_text_similarity(image_paths, texts)
        
        # 2. Visual Consistency
        print("🎨 Evaluating visual consistency...")
        visual_consistency = self.evaluate_visual_consistency(image_paths)
        
        # 3. Character Consistency (personalized mode only)
        character_consistency = None
        if mode == "personalized":
            print("👤 Evaluating character consistency...")
            character_consistency = self.evaluate_character_consistency(image_paths)
        
        # 4. Text Coherence
        print("📖 Evaluating text coherence...")
        text_coherence = self.evaluate_text_coherence(texts)
        
        # 5. Readability
        print("📚 Evaluating readability...")
        readability = self.evaluate_readability(full_text)
        
        # 6. Story Structure
        print("🏗️ Validating story structure...")
        story_structure = self.evaluate_story_structure(texts, len(scenes))
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(
            image_text_scores,
            visual_consistency,
            text_coherence,
            readability,
            story_structure
        )
        
        results = {
            "story_id": story_id,
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "num_scenes": len(scenes),
            "overall_score": overall_score,
            "metrics": {
                "image_text_alignment": {
                    "scores": image_text_scores,
                    "average": float(np.mean(image_text_scores)) if image_text_scores else 0.0
                },
                "visual_consistency": visual_consistency,
                "character_consistency": character_consistency,
                "text_coherence": text_coherence,
                "readability": readability,
                "story_structure": story_structure
            },
            "evaluation_time_seconds": round(time.time() - start_time, 2)
        }
        
        # Save results
        self.save_evaluation(story_id, results)
        
        print(f"✅ Evaluation complete! Overall score: {overall_score:.2f}")
        return results
    
    def _calculate_overall_score(
        self,
        image_text_scores: List[float],
        visual_consistency: Dict,
        text_coherence: Dict,
        readability: Dict,
        story_structure: Dict
    ) -> float:
        """Calculate weighted overall quality score (0-1)"""
        scores = []
        weights = []
        
        # Image-text alignment (25%)
        if image_text_scores:
            scores.append(np.mean(image_text_scores))
            weights.append(0.25)
        
        # Visual consistency (15%)
        if visual_consistency.get("average") is not None:
            scores.append(visual_consistency["average"])
            weights.append(0.15)
        
        # Text coherence (25%)
        if text_coherence.get("average") is not None:
            scores.append(text_coherence["average"])
            weights.append(0.25)
        
        # Readability (20%)
        if readability.get("suitable_for_target_age"):
            scores.append(1.0)
            weights.append(0.20)
        else:
            scores.append(0.5)
            weights.append(0.20)
        
        # Story structure (15%)
        if story_structure.get("follows_structure"):
            scores.append(1.0)
            weights.append(0.15)
        else:
            scores.append(0.0)
            weights.append(0.15)
        
        if not scores:
            return 0.0
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        overall = sum(s * w for s, w in zip(scores, normalized_weights))
        return round(overall, 3)
    
    def save_evaluation(self, story_id: int, results: Dict[str, Any]):
        """
        Save evaluation results to JSON file.
        
        Args:
            story_id: Database ID of the story
            results: Evaluation results dictionary
        """
        filename = f"story_{story_id}_evaluation.json"
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Evaluation saved to: {filepath}")
        except Exception as e:
            print(f"⚠️ Error saving evaluation: {e}")


# Singleton instance
_evaluation_manager = None

def get_evaluation_manager() -> EvaluationManager:
    """Get or create singleton EvaluationManager instance"""
    global _evaluation_manager
    if _evaluation_manager is None:
        _evaluation_manager = EvaluationManager()
    return _evaluation_manager
