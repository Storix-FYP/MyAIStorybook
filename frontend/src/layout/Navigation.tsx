'use client';

import React, { useState, useEffect } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/shared/components/ThemeToggle';
import './Navigation.css';

interface NavigationProps {
  onReset: () => void;
  showReset: boolean;
  onGoHome?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ onReset, showReset = false, onGoHome }) => {
  const [isScrolled, setIsScrolled] = useState<boolean>(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const { theme } = useTheme();

  useEffect(() => {
    const handleScroll = (): void => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: string): void => {
    if (sectionId === 'home' && onGoHome) {
      // If we're not on the landing page, use onGoHome to navigate back
      onGoHome();
    } else {
      // Otherwise, scroll to the section
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <nav className={`navigation ${isScrolled ? 'scrolled' : ''} ${theme}`}>
      <div className="nav-container">
        {/* Logo */}
        <div className="nav-logo" onClick={() => scrollToSection('home')}>
          <div className="logo-icon">📖</div>
          <span className="logo-text">MyAIStorybook</span>
        </div>

        {/* Desktop Menu */}
        <div className="nav-menu">
          <button 
            className="nav-link" 
            onClick={() => scrollToSection('home')}
          >
            Home
          </button>
          <button 
            className="nav-link" 
            onClick={() => scrollToSection('features')}
          >
            Features
          </button>
          <button 
            className="nav-link" 
            onClick={() => scrollToSection('about')}
          >
            About
          </button>
          <button 
            className="nav-link" 
            onClick={() => scrollToSection('contact')}
          >
            Contact
          </button>
          <ThemeToggle />
          {showReset && (
            <button 
              className="nav-link reset-link" 
              onClick={onReset}
            >
              New Story
            </button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-button"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle mobile menu"
        >
          <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${isMobileMenuOpen ? 'open' : ''}`}>
        <button 
          className="mobile-nav-link" 
          onClick={() => scrollToSection('home')}
        >
          Home
        </button>
        <button 
          className="mobile-nav-link" 
          onClick={() => scrollToSection('features')}
        >
          Features
        </button>
        <button 
          className="mobile-nav-link" 
          onClick={() => scrollToSection('about')}
        >
          About
        </button>
        <button 
          className="mobile-nav-link" 
          onClick={() => scrollToSection('contact')}
        >
          Contact
        </button>
        <div className="mobile-theme-toggle">
          <ThemeToggle />
        </div>
        {showReset && (
          <button 
            className="mobile-nav-link reset-link" 
            onClick={onReset}
          >
            New Story
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
