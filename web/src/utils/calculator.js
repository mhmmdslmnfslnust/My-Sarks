import { GradeScale } from '../models';

/**
 * Create and return the default grade scale
 */
export function createDefaultGradeScale() {
  return new GradeScale({
    0.20: ["A", 4.0],
    0.10: ["B+", 3.5],
    0.05: ["B", 3.0],
    0.00: ["C+", 2.5],
    -0.05: ["C", 2.0],
    -0.10: ["D+", 1.5],
    -0.15: ["D", 1.0],
    -0.20: ["F", 0.0]
  });
}

/**
 * Generate a summary for a subject with all calculations
 */
export function generateSubjectSummary(subject, gradeScale) {
  const [gradeLetter, gradePoints] = gradeScale.predictGrade(subject.overallRelativePerformance);
  
  return {
    name: subject.name,
    creditHours: subject.creditHours,
    myTotalRaw: subject.totalMyMarks,
    maxTotalRaw: subject.totalMaxMarks,
    classAvgRaw: subject.totalClassAvgMarks,
    myPercentage: subject.totalMaxMarks ? (subject.totalMyMarks / subject.totalMaxMarks) * 100 : 0,
    classAvgPercentage: subject.totalMaxMarks ? (subject.totalClassAvgMarks / subject.totalMaxMarks) * 100 : 0,
    weightedMyScore: subject.weightedTotalMyScore,
    weightedClassAvg: subject.weightedTotalClassAvg,
    relativePerformance: subject.overallRelativePerformance,
    relativePerformancePercentage: subject.overallRelativePerformance * 100,
    predictedGrade: gradeLetter,
    gradePoints: gradePoints,
    components: subject.components.map(comp => ({
      name: comp.name,
      weight: comp.weight,
      myMarks: comp.myMarks,
      maxMarks: comp.maxMarks,
      classAvgMarks: comp.classAvgMarks,
      myPercentage: comp.myPercentage,
      classAvgPercentage: comp.classAvgPercentage,
      weightedMyScore: comp.weightedMyScore,
      weightedClassAvg: comp.weightedClassAvg,
      relativePerformance: comp.relativePerformance,
      relativePerformancePercentage: comp.relativePerformance * 100
    }))
  };
}

/**
 * Generate a summary for a semester with all calculations
 */
export function generateSemesterSummary(semester, gradeScale) {
  const sgpa = semester.calculateSgpa(gradeScale);
  const cgpa = semester.calculateCgpa(gradeScale);
  
  return {
    name: semester.name,
    subjects: semester.subjects.map(subject => generateSubjectSummary(subject, gradeScale)),
    sgpa: sgpa,
    cgpa: semester.previousCgpa !== null ? cgpa : null,
    totalCredits: semester.subjects.reduce((sum, subject) => sum + subject.creditHours, 0),
    previousCgpa: semester.previousCgpa,
    previousCredits: semester.previousCredits
  };
}

// Define common presets for subjects
export const SUBJECT_PRESETS = {
  "Standard Academic": [
    { name: "Quizzes", weight: 10, count: 4, isGroup: true },
    { name: "Assignments", weight: 10, count: 2, isGroup: true },
    { name: "Mid-Semester Exam", weight: 30, count: 1, isGroup: false },
    { name: "End-Semester Exam", weight: 50, count: 1, isGroup: false },
  ],
  "Lab Course": [
    { name: "Lab Reports", weight: 30, count: 8, isGroup: true },
    { name: "Lab Performance", weight: 30, count: 1, isGroup: false },
    { name: "Lab Project", weight: 20, count: 1, isGroup: false },
    { name: "Lab Exam", weight: 20, count: 1, isGroup: false },
  ],
  "Project Based": [
    { name: "Progress Reports", weight: 20, count: 3, isGroup: true },
    { name: "Presentations", weight: 30, count: 2, isGroup: true },
    { name: "Final Project", weight: 40, count: 1, isGroup: false },
    { name: "Peer Review", weight: 10, count: 1, isGroup: false },
  ],
  "Custom": [] // Empty preset for manual entry
};
