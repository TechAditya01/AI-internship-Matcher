import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging
from extensions import db
from models import Student, Internship, Match


class InternshipMatchingEngine:
    def __init__(self):
        self.scaler = StandardScaler()

    def clear_matches_for_student(self, student_id):
        """Clear existing matches for a student (utility for testing)"""
        try:
            num_deleted = Match.query.filter_by(student_id=student_id).delete()
            db.session.commit()
            logging.info(f"Cleared {num_deleted} existing matches for student {student_id}")
        except Exception as e:
            logging.error(f"Error clearing matches for student {student_id}: {e}")
            db.session.rollback()
        
        
    def preprocess_skills(self, skills_text):
        """Convert comma-separated skills to clean text"""
        if not skills_text:
            return ""
        return " ".join([skill.strip().lower() for skill in skills_text.split(",")])
    
    def calculate_skills_similarity(self, student_skills, internship_skills):
        """Calculate cosine similarity between student and internship skills"""
        if not student_skills or not internship_skills:
            return 0.0
            
        try:
            # Combine student technical and soft skills
            student_text = self.preprocess_skills(student_skills)
            internship_text = self.preprocess_skills(internship_skills)
            
            if not student_text or not internship_text:
                return 0.0
            
            # Create TF-IDF vectors - use fresh vectorizer each time to avoid fitting conflicts
            texts = [student_text, internship_text]
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(min(similarity, 1.0))
            
        except Exception as e:
            logging.error(f"Error calculating skills similarity: {e}")
            return 0.0
    
    def calculate_location_score(self, student_preferred, student_current, internship_location):
        """Calculate location matching score"""
        if not internship_location:
            return 0.5
            
        score = 0.0
        internship_location = internship_location.lower()
        
        # Check preferred locations
        if student_preferred:
            preferred_list = [loc.strip().lower() for loc in student_preferred.split(",")]
            if any(pref in internship_location or internship_location in pref for pref in preferred_list):
                score += 0.8
        
        # Check current location
        if student_current and student_current.lower() in internship_location:
            score += 0.6
            
        # Remote work bonus
        if 'remote' in internship_location or 'work from home' in internship_location:
            score += 0.7
            
        return min(score, 1.0)
    
    def calculate_academic_score(self, student, internship):
        """Calculate academic compatibility score"""
        score = 0.0
        
        # CGPA scoring
        if student.cgpa and internship.min_cgpa:
            if student.cgpa >= internship.min_cgpa:
                # Bonus for exceeding minimum CGPA
                cgpa_ratio = student.cgpa / internship.min_cgpa
                score += min(cgpa_ratio * 0.4, 0.5)
            else:
                # Penalty for not meeting CGPA requirement
                score -= 0.3
        elif student.cgpa:
            # Default scoring if no minimum CGPA specified
            score += min(student.cgpa / 10.0 * 0.4, 0.4)
            
        # Course relevance
        if student.course and internship.preferred_course:
            if student.course.lower() in internship.preferred_course.lower() or \
               internship.preferred_course.lower() in student.course.lower():
                score += 0.3
                
        # Year of study compatibility
        if student.year_of_study and internship.year_of_study_requirement:
            year_req = internship.year_of_study_requirement.lower()
            student_year = student.year_of_study
            
            if 'any' in year_req or str(student_year) in year_req:
                score += 0.2
            elif 'final' in year_req and student_year >= 3:
                score += 0.2
            elif 'junior' in year_req and student_year <= 2:
                score += 0.2
                
        return max(0.0, min(score, 1.0))
    
    def calculate_affirmative_action_score(self, student, internship):
        """Calculate affirmative action bonus score"""
        score = 0.0
        
        # Social category consideration
        if student.social_category and student.social_category != 'General':
            category = student.social_category.upper()
            quota_field = f"{category.lower()}_quota"
            
            if hasattr(internship, quota_field):
                quota = getattr(internship, quota_field, 0)
                if quota > 0:
                    score += 0.3
                    
        # Rural/Aspirational district bonus
        if student.district_type:
            district_type = student.district_type.lower()
            if district_type in ['rural', 'aspirational']:
                if internship.rural_quota and internship.rural_quota > 0:
                    score += 0.25
                else:
                    # General rural bonus
                    score += 0.15
                    
        # First-time participant bonus
        if not student.pm_scheme_participant:
            score += 0.1
            
        # Limited previous internship experience bonus
        if student.previous_internships <= 1:
            score += 0.1
            
        return min(score, 1.0)
    
    def calculate_sector_interest_score(self, student_interests, internship_sector):
        """Calculate sector interest matching score"""
        if not student_interests or not internship_sector:
            return 0.5
            
        interests_list = [interest.strip().lower() for interest in student_interests.split(",")]
        sector_lower = internship_sector.lower()
        
        # Direct match
        if sector_lower in interests_list or any(interest in sector_lower for interest in interests_list):
            return 1.0
            
        # Partial match for related sectors
        related_matches = {
            'technology': ['software', 'it', 'tech', 'digital'],
            'finance': ['banking', 'financial', 'fintech'],
            'healthcare': ['medical', 'pharma', 'health'],
            'education': ['teaching', 'academic', 'research'],
            'marketing': ['advertising', 'sales', 'digital marketing']
        }
        
        for category, keywords in related_matches.items():
            if any(keyword in sector_lower for keyword in keywords):
                if category in interests_list:
                    return 0.8
                    
        return 0.3
    
    def generate_matches_for_student(self, student_id):
        """Generate matches for a specific student"""
        try:
            student = Student.query.get(student_id)
            if not student:
                logging.error(f"Student with ID {student_id} not found")
                return []

            # Get all active internships
            internships = Internship.query.filter_by(is_active=True).all()
            logging.info(f"Total active internships retrieved: {len(internships)}")

            matches = []
            skipped_full_capacity = 0
            skipped_existing_matches = 0
            
            for internship in internships:
                # Skip if internship is full
                if internship.filled_positions >= internship.total_positions:
                    skipped_full_capacity += 1
                    continue

                # Check if match already exists
                existing_match = Match.query.filter_by(
                    student_id=student_id, 
                    internship_id=internship.id
                ).first()

                if existing_match:
                    skipped_existing_matches += 1
                    continue

                # Calculate individual scores
                skills_score = self.calculate_skills_similarity(
                    (student.technical_skills or "") + " " + (student.soft_skills or ""),
                    internship.required_skills
                )

                location_score = self.calculate_location_score(
                    student.preferred_locations,
                    student.current_location,
                    internship.location
                )

                academic_score = self.calculate_academic_score(student, internship)

                affirmative_action_score = self.calculate_affirmative_action_score(student, internship)

                sector_score = self.calculate_sector_interest_score(
                    student.sector_interests,
                    internship.sector
                )

                # Weighted overall score
                weights = {
                    'skills': 0.35,
                    'academic': 0.25,
                    'location': 0.20,
                    'sector': 0.15,
                    'affirmative_action': 0.05
                }

                overall_score = float(
                    skills_score * weights['skills'] +
                    academic_score * weights['academic'] +
                    location_score * weights['location'] +
                    sector_score * weights['sector'] +
                    affirmative_action_score * weights['affirmative_action']
                )

                # Only create matches above threshold
                if overall_score >= 0.3:
                    match = Match(
                        student_id=student_id,
                        internship_id=internship.id,
                        overall_score=float(overall_score),
                        skills_score=float(skills_score),
                        location_score=float(location_score),
                        academic_score=float(academic_score),
                        affirmative_action_score=float(affirmative_action_score)
                    )
                    matches.append(match)

            logging.info(f"Skipped {skipped_full_capacity} internships due to capacity")
            logging.info(f"Skipped {skipped_existing_matches} internships due to existing matches")
            
            # Save matches to database
            try:
                for match in matches:
                    db.session.add(match)
                db.session.commit()
            except Exception as commit_error:
                logging.error(f"Database commit error when saving matches for student {student_id}: {commit_error}")
                db.session.rollback()
                return []

            # Return sorted matches (best first)
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            return matches

        except Exception as e:
            logging.error(f"Error generating matches for student {student_id}: {e}")
            db.session.rollback()
            return []
    
    def calculate_match_percentage(self, student, internship):
        """Calculate match percentage between a student and internship (on-demand)"""
        try:
            # Calculate individual scores using existing methods
            skills_score = self.calculate_skills_similarity(
                (student.technical_skills or "") + " " + (student.soft_skills or ""),
                internship.required_skills
            )
            
            location_score = self.calculate_location_score(
                student.preferred_locations,
                student.current_location,
                internship.location
            )
            
            academic_score = self.calculate_academic_score(student, internship)
            
            affirmative_action_score = self.calculate_affirmative_action_score(student, internship)
            
            sector_score = self.calculate_sector_interest_score(
                student.sector_interests,
                internship.sector
            )
            
            # Weighted overall score (same weights as in generate_matches_for_student)
            weights = {
                'skills': 0.35,
                'academic': 0.25,
                'location': 0.20,
                'sector': 0.15,
                'affirmative_action': 0.05
            }
            
            overall_score = float(
                skills_score * weights['skills'] +
                academic_score * weights['academic'] +
                location_score * weights['location'] +
                sector_score * weights['sector'] +
                affirmative_action_score * weights['affirmative_action']
            )
            
            # Return percentage (0-100)
            return round(overall_score * 100, 1)
            
        except Exception as e:
            logging.error(f"Error calculating match percentage: {e}")
            return 0.0

    def generate_all_matches(self):
        """Generate matches for all students"""
        try:
            students = Student.query.all()
            total_matches = 0
            
            for student in students:
                matches = self.generate_matches_for_student(student.id)
                total_matches += len(matches)
                logging.info(f"Generated {len(matches)} matches for student {student.name}")
            
            logging.info(f"Total matches generated: {total_matches}")
            return total_matches
            
        except Exception as e:
            logging.error(f"Error generating all matches: {e}")
            return 0
