import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging

from app.extensions import db
from app.models import Student, Internship, Match


class InternshipMatchingEngine:
    def __init__(self):
        self.scaler = StandardScaler()

    def clear_matches_for_student(self, student_id):
        """Clear existing matches for a student"""
        try:
            num_deleted = Match.query.filter_by(student_id=student_id).delete(synchronize_session=False)
            db.session.commit()
            logging.info(f"Cleared {num_deleted} existing matches for student {student_id}")
        except Exception as e:
            logging.error(f"Error clearing matches for student {student_id}: {e}")
            db.session.rollback()

    def preprocess_skills(self, skills_text):
        """Normalize comma-separated skills"""
        if not skills_text:
            return ""
        return " ".join(s.strip().lower() for s in skills_text.split(","))

    def calculate_skills_similarity(self, student_skills, internship_skills):
        """Cosine similarity score"""
        if not student_skills or not internship_skills:
            return 0.0

        try:
            student_text = self.preprocess_skills(student_skills)
            internship_text = self.preprocess_skills(internship_skills)

            if not student_text or not internship_text:
                return 0.0

            vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
            tfidf = vectorizer.fit_transform([student_text, internship_text])

            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(min(sim, 1.0))
        except Exception as e:
            logging.error(f"Skill similarity error: {e}")
            return 0.0

    def calculate_location_score(self, preferred, current, internship_loc):
        """Location matching score"""
        if not internship_loc:
            return 0.5

        score = 0.0
        internship_loc = internship_loc.lower()

        if preferred:
            pref_list = [p.strip().lower() for p in preferred.split(",")]
            if any(p in internship_loc for p in pref_list):
                score += 0.8

        if current and current.lower() in internship_loc:
            score += 0.6

        if "remote" in internship_loc or "work from home" in internship_loc:
            score += 0.7

        return min(score, 1.0)

    def calculate_academic_score(self, student, internship):
        score = 0.0

        if student.cgpa and internship.min_cgpa:
            if student.cgpa >= internship.min_cgpa:
                score += min((student.cgpa / internship.min_cgpa) * 0.4, 0.5)
            else:
                score -= 0.3
        elif student.cgpa:
            score += min(student.cgpa / 10 * 0.4, 0.4)

        if student.course and internship.preferred_course:
            if student.course.lower() in internship.preferred_course.lower():
                score += 0.3

        if student.year_of_study and internship.year_of_study_requirement:
            req = internship.year_of_study_requirement.lower()
            year = student.year_of_study

            if "any" in req or str(year) in req:
                score += 0.2
            elif "final" in req and year >= 3:
                score += 0.2
            elif "junior" in req and year <= 2:
                score += 0.2

        return max(0, min(score, 1.0))

    def calculate_affirmative_action_score(self, student, internship):
        score = 0.0

        if student.social_category and student.social_category != "General":
            quota = getattr(internship, f"{student.social_category.lower()}_quota", 0)
            if quota > 0:
                score += 0.3

        if student.district_type and student.district_type.lower() in ["rural", "aspirational"]:
            score += 0.25 if internship.rural_quota > 0 else 0.15

        if not student.pm_scheme_participant:
            score += 0.1

        if student.previous_internships <= 1:
            score += 0.1

        return min(score, 1.0)

    def calculate_sector_interest_score(self, interests, sector):
        if not interests or not sector:
            return 0.5

        interests = [i.strip().lower() for i in interests.split(",")]
        sector_lower = sector.lower()

        if sector_lower in interests:
            return 1.0

        related = {
            "technology": ["software", "it", "tech"],
            "finance": ["banking", "fintech"],
            "healthcare": ["medical", "pharma"],
        }

        for category, keywords in related.items():
            if any(k in sector_lower for k in keywords) and category in interests:
                return 0.8

        return 0.3

    def generate_matches_for_student(self, student_id):
        try:
            student = Student.query.get(student_id)
            if not student:
                logging.error(f"Student {student_id} not found")
                return []

            internships = Internship.query.filter_by(is_active=True).all()
            matches = []

            for internship in internships:

                if internship.filled_positions >= internship.total_positions:
                    continue

                if Match.query.filter_by(student_id=student_id, internship_id=internship.id).first():
                    continue

                scores = {
                    "skills": self.calculate_skills_similarity(
                        f"{student.technical_skills} {student.soft_skills}",
                        internship.required_skills,
                    ),
                    "location": self.calculate_location_score(
                        student.preferred_locations,
                        student.current_location,
                        internship.location,
                    ),
                    "academic": self.calculate_academic_score(student, internship),
                    "affirmative": self.calculate_affirmative_action_score(student, internship),
                    "sector": self.calculate_sector_interest_score(
                        student.sector_interests, internship.sector
                    ),
                }

                weights = {"skills": 0.35, "academic": 0.25, "location": 0.20, "sector": 0.15, "affirmative": 0.05}

                overall = sum(scores[k] * w for k, w in weights.items())

                if overall >= 0.3:
                    matches.append(
                        Match(
                            student_id=student_id,
                            internship_id=internship.id,
                            overall_score=float(overall),
                            skills_score=scores["skills"],
                            location_score=scores["location"],
                            academic_score=scores["academic"],
                            affirmative_action_score=scores["affirmative"],
                        )
                    )

            db.session.add_all(matches)
            db.session.commit()

            return sorted(matches, key=lambda x: x.overall_score, reverse=True)

        except Exception as e:
            logging.error(f"Matching error: {e}")
            db.session.rollback()
            return []

    def generate_all_matches(self):
        try:
            students = Student.query.all()
            count = sum(len(self.generate_matches_for_student(s.id)) for s in students)
            return count
        except Exception as e:
            logging.error(f"Bulk match error: {e}")
            return 0
