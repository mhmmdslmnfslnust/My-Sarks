/**
 * Component class representing a graded component of a subject
 */
export class Component {
  constructor(name, weight, maxMarks, myMarks, classAvgMarks) {
    this.name = name;
    this.weight = weight;  // Weight as a percentage (0-100)
    this.maxMarks = maxMarks;
    this.myMarks = myMarks;
    this.classAvgMarks = classAvgMarks;
  }

  get myPercentage() {
    return (this.myMarks / this.maxMarks) * 100;
  }

  get classAvgPercentage() {
    return (this.classAvgMarks / this.maxMarks) * 100;
  }
  
  get weightedMyScore() {
    return (this.myMarks / this.maxMarks) * this.weight;
  }
  
  get weightedClassAvg() {
    return (this.classAvgMarks / this.maxMarks) * this.weight;
  }
  
  get relativePerformance() {
    if (this.classAvgMarks === 0) {
      return 0;
    }
    return (this.myMarks - this.classAvgMarks) / this.classAvgMarks;
  }
}

/**
 * Subject class representing a course with multiple components
 */
export class Subject {
  constructor(name, creditHours, components = []) {
    this.name = name;
    this.creditHours = creditHours;
    this.components = components;
  }
  
  get totalMyMarks() {
    return this.components.reduce((sum, comp) => sum + comp.myMarks, 0);
  }
  
  get totalMaxMarks() {
    return this.components.reduce((sum, comp) => sum + comp.maxMarks, 0);
  }
  
  get totalClassAvgMarks() {
    return this.components.reduce((sum, comp) => sum + comp.classAvgMarks, 0);
  }
  
  get weightedTotalMyScore() {
    return this.components.reduce((sum, comp) => sum + comp.weightedMyScore, 0);
  }
  
  get weightedTotalClassAvg() {
    return this.components.reduce((sum, comp) => sum + comp.weightedClassAvg, 0);
  }
  
  get overallRelativePerformance() {
    if (this.weightedTotalClassAvg === 0) {
      return 0;
    }
    return (this.weightedTotalMyScore - this.weightedTotalClassAvg) / this.weightedTotalClassAvg;
  }
}

/**
 * GradeScale class for determining grades based on relative performance
 */
export class GradeScale {
  constructor(thresholds) {
    this.thresholds = thresholds;
  }
  
  predictGrade(relativePerformance) {
    // Get all thresholds as numbers and sort them in descending order
    const thresholdValues = Object.keys(this.thresholds)
      .map(Number)
      .sort((a, b) => b - a);
    
    for (const threshold of thresholdValues) {
      if (relativePerformance >= threshold) {
        return this.thresholds[threshold];
      }
    }
    
    // If no threshold is met, return the lowest grade
    const minThreshold = Math.min(...thresholdValues);
    return this.thresholds[minThreshold];
  }
}

/**
 * Semester class representing a collection of subjects in one semester
 */
export class Semester {
  constructor(name, subjects = [], previousCgpa = null, previousCredits = null) {
    this.name = name;
    // Ensure subjects is always an array
    this.subjects = Array.isArray(subjects) ? subjects : [];
    this.previousCgpa = previousCgpa;
    this.previousCredits = previousCredits;
  }
  
  calculateSgpa(gradeScale) {
    let totalCreditPoints = 0;
    let totalCredits = 0;
    
    // Defensive check to ensure subjects exists and is iterable
    if (!this.subjects || !Array.isArray(this.subjects) || this.subjects.length === 0) {
      console.warn("No subjects found or subjects is not an array in calculateSgpa");
      return 0;
    }
    
    try {
      // Calculate total credits for denominator
      totalCredits = this.subjects.reduce((sum, subject) => {
        // Ensure subject is valid and has creditHours that's a number
        const creditHours = subject && typeof subject.creditHours === 'number' ? subject.creditHours : 0;
        return sum + creditHours;
      }, 0);
      
      if (totalCredits === 0) {
        return 0;
      }
      
      // Calculate credit points safely
      for (const subject of this.subjects) {
        if (!subject) continue; // Skip invalid subjects
        
        try {
          const creditHours = subject.creditHours || 0;
          // Only process if subject has necessary properties
          if (subject.overallRelativePerformance !== undefined && creditHours > 0) {
            const [, gradePoints] = gradeScale.predictGrade(subject.overallRelativePerformance);
            totalCreditPoints += gradePoints * creditHours;
          }
        } catch (error) {
          console.error("Error processing subject in calculateSgpa:", error, subject);
          // Continue processing other subjects
        }
      }
      
      return totalCreditPoints / totalCredits;
    } catch (error) {
      console.error("Error in calculateSgpa:", error);
      return 0; // Return a safe default
    }
  }
  
  calculateCgpa(gradeScale) {
    if (this.previousCgpa === null || this.previousCredits === null) {
      return this.calculateSgpa(gradeScale);
    }
    
    try {
      const sgpa = this.calculateSgpa(gradeScale);
      const currentCredits = this.subjects?.reduce((sum, subject) => sum + (subject?.creditHours || 0), 0) || 0;
      
      const totalCredits = (this.previousCredits || 0) + currentCredits;
      if (totalCredits === 0) return 0;
      
      const totalPoints = ((this.previousCgpa || 0) * (this.previousCredits || 0)) + (sgpa * currentCredits);
      
      return totalPoints / totalCredits;
    } catch (error) {
      console.error("Error in calculateCgpa:", error);
      return 0; // Return a safe default
    }
  }
}
