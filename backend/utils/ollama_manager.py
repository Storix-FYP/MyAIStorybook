# backend/utils/ollama_manager.py
"""
Utility to manage Ollama service during image generation
Pauses Ollama to free up GPU memory for faster image generation
"""

import subprocess
import time
import psutil
import os


class OllamaManager:
    """Manages Ollama service state"""
    
    @staticmethod
    def is_ollama_running() -> bool:
        """Check if Ollama process is running"""
        for proc in psutil.process_iter(['name']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    @staticmethod
    def pause_ollama():
        """Stop Ollama service to free GPU memory - Windows-specific forceful kill"""
        try:
            if OllamaManager.is_ollama_running():
                print("[OllamaManager] 🛑 Pausing Ollama to free GPU memory...")
                
                # Windows-specific: Use taskkill to forcefully terminate
                try:
                    # Kill all ollama processes forcefully
                    result = subprocess.run(
                        ["taskkill", "/F", "/IM", "ollama.exe", "/T"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    print(f"[OllamaManager] taskkill output: {result.stdout}")
                except Exception as e:
                    print(f"[OllamaManager] taskkill error: {e}")
                
                # Also try psutil kill as backup
                killed_count = 0
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        if 'ollama' in proc.info['name'].lower():
                            print(f"[OllamaManager] Killing Ollama process (PID: {proc.info['pid']})")
                            proc.kill()
                            proc.wait(timeout=3)  # Wait for process to die
                            killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        continue
                
                # Wait longer for GPU memory to be freed
                time.sleep(5)  # Increased wait time for GPU cleanup
                
                # Force GPU memory cleanup
                try:
                    import torch
                    if torch.cuda.is_available():
                        print("[OllamaManager] Clearing GPU cache...")
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                        print("[OllamaManager] ✅ GPU cache cleared")
                except Exception as e:
                    print(f"[OllamaManager] ⚠️ Could not clear GPU cache: {e}")
                
                # Verify Ollama is actually stopped
                if OllamaManager.is_ollama_running():
                    print("[OllamaManager] ⚠️ WARNING: Ollama still running after kill attempt!")
                    return False
                else:
                    print(f"[OllamaManager] ✅ Ollama KILLED ({killed_count} process(es) terminated)")
                    return True
            else:
                print("[OllamaManager] Ollama not running, nothing to pause")
                return False
        except Exception as e:
            print(f"[OllamaManager] ⚠️ Could not pause Ollama: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def resume_ollama():
        """Resume Ollama service"""
        try:
            if not OllamaManager.is_ollama_running():
                print("[OllamaManager] ▶️ Resuming Ollama...")
                
                # Clear GPU cache before starting Ollama for faster startup
                try:
                    import torch
                    if torch.cuda.is_available():
                        print("[OllamaManager] Clearing GPU cache before Ollama resume...")
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                        print("[OllamaManager] ✅ GPU cache cleared")
                except Exception as e:
                    print(f"[OllamaManager] ⚠️ Could not clear GPU cache: {e}")
                
                # Ollama will auto-start on next request
                # We start it in background
                subprocess.Popen(
                    ["ollama", "serve"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                time.sleep(3)  # Wait for Ollama to start
                print("[OllamaManager] ✅ Ollama resumed")
                return True
            else:
                print("[OllamaManager] Ollama already running")
                return False
        except Exception as e:
            print(f"[OllamaManager] ⚠️ Could not resume Ollama: {e}")
            return False


def with_ollama_paused(func):
    """Decorator to pause Ollama during function execution"""
    def wrapper(*args, **kwargs):
        was_running = OllamaManager.pause_ollama()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            if was_running:
                OllamaManager.resume_ollama()
    return wrapper
