import json
from typing import List, Optional

from models import Component, GradeScale, Subject, Semester
from calculator import create_default_grade_scale, generate_semester_summary


def get_float_input(prompt: str, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
    """Get a float input from the user with validation"""
    while True:
        try:
            value = float(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def get_yes_no_input(prompt: str) -> bool:
    """Get a yes/no input from the user"""
    while True:
        response = input(prompt + " (y/n): ").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'.")


def create_component() -> Component:
    """Get component details from the user"""
    print("\n=== New Component ===")
    name = input("Component name (e.g., Quiz 1, Assignment 2): ")
    weight = get_float_input("Weight in final grade (0-100): ", 0, 100)
    max_marks = get_float_input("Maximum possible marks: ", 0)
    my_marks = get_float_input(f"Your marks (0-{max_marks}): ", 0, max_marks)
    class_avg_marks = get_float_input(f"Class average marks (0-{max_marks}): ", 0, max_marks)
    
    return Component(name, weight, max_marks, my_marks, class_avg_marks)


def create_subject() -> Subject:
    """Get subject details from the user"""
    print("\n=== New Subject ===")
    name = input("Subject name: ")
    credit_hours = get_float_input("Credit hours: ", 0)
    
    components = []
    total_weight = 0
    
    print("\nNow enter the components for this subject (quizzes, assignments, exams, etc.)")
    print("The total weight should add up to 100%")
    
    while True:
        component = create_component()
        components.append(component)
        total_weight += component.weight
        
        print(f"Current total weight: {total_weight}%")
        
        if total_weight >= 100:
            if total_weight > 100:
                print("Warning: Total weight exceeds 100%. The weights will be normalized.")
                # Normalize weights
                for comp in components:
                    comp.weight = (comp.weight / total_weight) * 100
            break
        
        if not get_yes_no_input("Add another component?"):
            if total_weight < 100:
                print(f"Warning: Total weight is only {total_weight}%. The weights will be normalized.")
                # Normalize weights
                for comp in components:
                    comp.weight = (comp.weight / total_weight) * 100
            break
    
    return Subject(name, credit_hours, components)


def create_semester() -> Semester:
    """Get semester details from the user"""
    print("\n=== New Semester ===")
    name = input("Semester name/number: ")
    
    subjects = []
    while True:
        subjects.append(create_subject())
        if not get_yes_no_input("Add another subject?"):
            break
    
    previous_cgpa = None
    previous_credits = None
    if get_yes_no_input("Do you want to include previous CGPA data?"):
        previous_cgpa = get_float_input("Previous CGPA: ", 0, 4.0)
        previous_credits = get_float_input("Previous total credit hours: ", 0)
    
    return Semester(name, subjects, previous_cgpa, previous_credits)


def display_subject_summary(subject_summary: dict, grade_scale: GradeScale):
    """Display a summary for a subject"""
    print(f"\n{'=' * 60}")
    print(f"Subject: {subject_summary['name']} ({subject_summary['credit_hours']} credits)")
    print(f"{'=' * 60}")
    
    print("\nComponent Breakdown:")
    print(f"{'Component':<15} {'Weight':<10} {'My Score':<15} {'Class Avg':<15} {'Relative':<10}")
    print(f"{'-' * 15} {'-' * 10} {'-' * 15} {'-' * 15} {'-' * 10}")
    
    for comp in subject_summary['components']:
        print(f"{comp['name']:<15} {comp['weight']:<10.1f}% "
              f"{comp['my_marks']}/{comp['max_marks']} ({comp['my_percentage']:.1f}%) "
              f"{comp['class_avg_marks']}/{comp['max_marks']} ({comp['class_avg_percentage']:.1f}%) "
              f"{comp['relative_performance_percentage']:+.1f}%")
    
    print(f"\nOverall:")
    print(f"My weighted total: {subject_summary['weighted_my_score']:.1f}/100")
    print(f"Class average: {subject_summary['weighted_class_avg']:.1f}/100")
    print(f"Relative performance: {subject_summary['relative_performance_percentage']:+.1f}%")
    
    print(f"\nPredicted Grade: {subject_summary['predicted_grade']} ({subject_summary['grade_points']} points)")


def display_semester_summary(semester_summary: dict, grade_scale: GradeScale):
    """Display a summary for a semester"""
    print(f"\n{'#' * 70}")
    print(f"Semester: {semester_summary['name']}")
    print(f"{'#' * 70}")
    
    for subject in semester_summary['subjects']:
        display_subject_summary(subject, grade_scale)
    
    print(f"\n{'#' * 70}")
    print(f"Semester GPA (SGPA): {semester_summary['sgpa']:.2f}")
    if semester_summary['cgpa'] is not None:
        print(f"Cumulative GPA (CGPA): {semester_summary['cgpa']:.2f}")
    print(f"{'#' * 70}")


def customize_grade_scale(grade_scale: GradeScale) -> GradeScale:
    """Allow the user to customize the grade scale"""
    print("\n=== Customize Grade Scale ===")
    print("Current grade scale:")
    thresholds = {}
    
    for threshold, (grade, points) in sorted(grade_scale.thresholds.items(), reverse=True):
        print(f"{threshold*100:+.0f}% relative to average: {grade} ({points} points)")
    
    if get_yes_no_input("Do you want to customize this scale?"):
        print("\nEnter new threshold values (as percentages):")
        thresholds[get_float_input("A (4.0) threshold (%): ", None, None) / 100] = ("A", 4.0)
        thresholds[get_float_input("B+ (3.5) threshold (%): ", None, None) / 100] = ("B+", 3.5)
        thresholds[get_float_input("B (3.0) threshold (%): ", None, None) / 100] = ("B", 3.0)
        thresholds[get_float_input("C+ (2.5) threshold (%): ", None, None) / 100] = ("C+", 2.5)
        thresholds[get_float_input("C (2.0) threshold (%): ", None, None) / 100] = ("C", 2.0)
        thresholds[get_float_input("D+ (1.5) threshold (%): ", None, None) / 100] = ("D+", 1.5)
        thresholds[get_float_input("D (1.0) threshold (%): ", None, None) / 100] = ("D", 1.0)
        thresholds[get_float_input("F (0.0) threshold (%): ", None, None) / 100] = ("F", 0.0)
        return GradeScale(thresholds)
    else:
        return grade_scale


def save_to_file(semester_summary: dict, filename: str):
    """Save the semester summary to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(semester_summary, f, indent=2)
    print(f"\nSummary saved to {filename}")


def run_cli():
    """Run the command-line interface"""
    print("Welcome to the Academic Performance Tracker!")
    grade_scale = customize_grade_scale(create_default_grade_scale())
    
    semester = create_semester()
    semester_summary = generate_semester_summary(semester, grade_scale)
    
    display_semester_summary(semester_summary, grade_scale)
    
    if get_yes_no_input("Do you want to save this summary to a file?"):
        filename = input("Enter filename (default: academic_summary.json): ") or "academic_summary.json"
        save_to_file(semester_summary, filename)
