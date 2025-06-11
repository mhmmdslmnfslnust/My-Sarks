from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Component:
    name: str
    weight: float  # Weight as a percentage (0-100)
    max_marks: float
    my_marks: float
    class_avg_marks: float

    @property
    def my_percentage(self) -> float:
        return (self.my_marks / self.max_marks) * 100

    @property
    def class_avg_percentage(self) -> float:
        return (self.class_avg_marks / self.max_marks) * 100
    
    @property
    def weighted_my_score(self) -> float:
        return (self.my_marks / self.max_marks) * self.weight
    
    @property
    def weighted_class_avg(self) -> float:
        return (self.class_avg_marks / self.max_marks) * self.weight
    
    @property
    def relative_performance(self) -> float:
        if self.class_avg_marks == 0:
            return 0
        return (self.my_marks - self.class_avg_marks) / self.class_avg_marks


@dataclass
class Subject:
    name: str
    credit_hours: float
    components: List[Component] = field(default_factory=list)
    
    @property
    def total_my_marks(self) -> float:
        return sum(comp.my_marks for comp in self.components)
    
    @property
    def total_max_marks(self) -> float:
        return sum(comp.max_marks for comp in self.components)
    
    @property
    def total_class_avg_marks(self) -> float:
        return sum(comp.class_avg_marks for comp in self.components)
    
    @property
    def weighted_total_my_score(self) -> float:
        return sum(comp.weighted_my_score for comp in self.components)
    
    @property
    def weighted_total_class_avg(self) -> float:
        return sum(comp.weighted_class_avg for comp in self.components)
    
    @property
    def overall_relative_performance(self) -> float:
        if self.weighted_total_class_avg == 0:
            return 0
        return (self.weighted_total_my_score - self.weighted_total_class_avg) / self.weighted_total_class_avg


@dataclass
class GradeScale:
    thresholds: Dict[float, tuple]
    
    def predict_grade(self, relative_performance: float) -> tuple:
        """Returns a tuple of (grade_letter, grade_points) based on relative performance"""
        for threshold, grade in sorted(self.thresholds.items(), reverse=True):
            if relative_performance >= threshold:
                return grade
        # If no threshold is met, return the lowest grade
        return self.thresholds[min(self.thresholds.keys())]


@dataclass
class Semester:
    name: str
    subjects: List[Subject] = field(default_factory=list)
    previous_cgpa: Optional[float] = None
    previous_credits: Optional[float] = None
    
    def calculate_sgpa(self, grade_scale: GradeScale) -> float:
        """Calculate SGPA for the semester"""
        total_credit_points = 0
        total_credits = sum(subject.credit_hours for subject in self.subjects)
        
        if total_credits == 0:
            return 0
        
        for subject in self.subjects:
            _, grade_points = grade_scale.predict_grade(subject.overall_relative_performance)
            total_credit_points += grade_points * subject.credit_hours
            
        return total_credit_points / total_credits
    
    def calculate_cgpa(self, grade_scale: GradeScale) -> float:
        """Calculate CGPA including previous semesters if available"""
        if self.previous_cgpa is None or self.previous_credits is None:
            return self.calculate_sgpa(grade_scale)
        
        sgpa = self.calculate_sgpa(grade_scale)
        current_credits = sum(subject.credit_hours for subject in self.subjects)
        
        total_credits = self.previous_credits + current_credits
        total_points = (self.previous_cgpa * self.previous_credits) + (sgpa * current_credits)
        
        return total_points / total_credits
