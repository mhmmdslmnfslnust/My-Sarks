from typing import Dict

from models import GradeScale, Subject, Semester


def create_default_grade_scale() -> GradeScale:
    """Create and return the default grade scale as specified in requirements"""
    # Updated grade scale to make C+ and B around the average
    return GradeScale({
        0.30: ("A", 4.0),    # +30% above average (>2 standard deviations)
        0.20: ("A-", 3.7),   # +20% above average (>1.5 standard deviations)
        0.15: ("B+", 3.3),   # +15% above average (>1 standard deviation)
        0.05: ("B", 3.0),    # +5% above average (around 0.5 standard deviation)
        -0.05: ("C+", 2.7),  # -5% below average to +5% above (within 0.5 standard deviation)
        -0.15: ("C", 2.3),   # -15% below average (around 1 standard deviation below)
        -0.25: ("D", 1.0),   # -25% below average (around 1.5 standard deviations below)
        -0.35: ("F", 0.0)    # -35% or more below average (>2 standard deviations below)
    })


def generate_subject_summary(subject: Subject, grade_scale: GradeScale) -> Dict:
    """Generate a summary dictionary for a subject with all relevant calculations"""
    grade_letter, grade_points = grade_scale.predict_grade(subject.overall_relative_performance)
    
    return {
        "name": subject.name,
        "credit_hours": subject.credit_hours,
        "my_total_raw": subject.total_my_marks,
        "max_total_raw": subject.total_max_marks,
        "class_avg_raw": subject.total_class_avg_marks,
        "my_percentage": (subject.total_my_marks / subject.total_max_marks) * 100 if subject.total_max_marks else 0,
        "class_avg_percentage": (subject.total_class_avg_marks / subject.total_max_marks) * 100 if subject.total_max_marks else 0,
        "weighted_my_score": subject.weighted_total_my_score,
        "weighted_class_avg": subject.weighted_total_class_avg,
        "relative_performance": subject.overall_relative_performance,
        "relative_performance_percentage": subject.overall_relative_performance * 100,
        "predicted_grade": grade_letter,
        "grade_points": grade_points,
        "components": [
            {
                "name": comp.name,
                "weight": comp.weight,
                "my_marks": comp.my_marks,
                "max_marks": comp.max_marks,
                "class_avg_marks": comp.class_avg_marks,
                "my_percentage": comp.my_percentage,
                "class_avg_percentage": comp.class_avg_percentage,
                "weighted_my_score": comp.weighted_my_score,
                "weighted_class_avg": comp.weighted_class_avg,
                "relative_performance": comp.relative_performance,
                "relative_performance_percentage": comp.relative_performance * 100
            }
            for comp in subject.components
        ]
    }


def generate_semester_summary(semester: Semester, grade_scale: GradeScale) -> Dict:
    """Generate a summary dictionary for a semester with all relevant calculations"""
    sgpa = semester.calculate_sgpa(grade_scale)
    cgpa = semester.calculate_cgpa(grade_scale)
    
    return {
        "name": semester.name,
        "subjects": [generate_subject_summary(subject, grade_scale) for subject in semester.subjects],
        "sgpa": sgpa,
        "cgpa": cgpa if semester.previous_cgpa is not None else None,
        "total_credits": sum(subject.credit_hours for subject in semester.subjects),
        "previous_cgpa": semester.previous_cgpa,
        "previous_credits": semester.previous_credits
    }
