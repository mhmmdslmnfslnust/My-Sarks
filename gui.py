import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, List, Optional, Tuple

from models import Component, Subject, Semester, GradeScale
from calculator import create_default_grade_scale, generate_semester_summary

class ScrollableFrame(ttk.Frame):
    """A scrollable frame widget"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class GradeScaleScreen(ttk.Frame):
    """Screen for customizing the grade scale"""
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.parent = parent
        self.on_complete = on_complete
        self.grade_scale = create_default_grade_scale()
        self.grade_entries = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        ttk.Label(self, text="Customize Grade Scale", font=("TkDefaultFont", 14, "bold")).pack(pady=10)
        ttk.Label(self, text="Enter relative performance thresholds (as percentages)").pack(pady=5)
        
        # Create input fields for each grade
        grades = [
            ("A", 4.0), ("B+", 3.5), ("B", 3.0), ("C+", 2.5),
            ("C", 2.0), ("D+", 1.5), ("D", 1.0), ("F", 0.0)
        ]
        
        entry_frame = ttk.Frame(self)
        entry_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get current thresholds for display
        current_thresholds = {}
        for threshold, (grade, _) in self.grade_scale.thresholds.items():
            current_thresholds[grade] = threshold * 100
            
        # Create entry fields
        for i, (grade, points) in enumerate(grades):
            row = ttk.Frame(entry_frame)
            row.pack(fill="x", pady=5)
            
            # Label
            ttk.Label(row, text=f"{grade} ({points} points) threshold:", width=20).pack(side="left")
            
            # Entry with default value
            var = tk.StringVar(value=str(current_thresholds.get(grade, 0)))
            entry = ttk.Entry(row, textvariable=var, width=10)
            entry.pack(side="left", padx=5)
            ttk.Label(row, text="%").pack(side="left")
            
            self.grade_entries[grade] = var
        
        # Add buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=20)
        
        ttk.Button(btn_frame, text="Use Default Scale", 
                   command=self.use_default).pack(side="left", padx=10)
                   
        ttk.Button(btn_frame, text="Continue", 
                   command=self.save_and_continue).pack(side="right", padx=10)
        
    def use_default(self):
        """Reset to default grade scale"""
        self.grade_scale = create_default_grade_scale()
        self.on_complete(self.grade_scale)
        
    def save_and_continue(self):
        """Save custom grade scale and continue"""
        try:
            thresholds = {}
            for grade, entry_var in self.grade_entries.items():
                percentage = float(entry_var.get())
                # Convert percentage to decimal
                threshold = percentage / 100
                
                # Find corresponding grade points
                grade_points = next((points for g, points in self.grade_scale.thresholds.values() if g == grade), 0)
                thresholds[threshold] = (grade, grade_points)
                
            custom_grade_scale = GradeScale(thresholds)
            self.on_complete(custom_grade_scale)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all thresholds.")

class SubjectEntryScreen(ttk.Frame):
    """Screen for entering subject details"""
    def __init__(self, parent, grade_scale, on_complete):
        super().__init__(parent)
        self.parent = parent
        self.grade_scale = grade_scale
        self.on_complete = on_complete
        self.subjects = []
        self.cgpa_var = tk.StringVar(value="")
        self.credits_var = tk.StringVar(value="")
        self.include_previous_var = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        ttk.Label(self, text="Subject Entry", font=("TkDefaultFont", 14, "bold")).pack(pady=10)
        
        # Frame for previous CGPA
        cgpa_frame = ttk.LabelFrame(self, text="Previous CGPA (Optional)")
        cgpa_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Checkbutton(cgpa_frame, text="Include previous CGPA data", 
                      variable=self.include_previous_var).pack(anchor="w", pady=5, padx=10)
        
        row = ttk.Frame(cgpa_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text="Previous CGPA:").pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.cgpa_var, width=10).pack(side="left", padx=5)
        
        row = ttk.Frame(cgpa_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text="Previous Credits:").pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.credits_var, width=10).pack(side="left", padx=5)
        
        # Frame for subjects list
        self.subjects_frame = ScrollableFrame(self)
        self.subjects_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # No subjects message
        self.no_subjects_label = ttk.Label(
            self.subjects_frame.scrollable_frame, 
            text="No subjects added yet. Click 'Add Subject' to begin."
        )
        self.no_subjects_label.pack(pady=20)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10, padx=20)
        
        ttk.Button(btn_frame, text="Add Subject", 
                 command=self.add_subject).pack(side="left")
                 
        ttk.Button(btn_frame, text="Calculate Results", 
                 command=self.save_and_continue).pack(side="right")
    
    def update_subjects_display(self):
        """Update the UI to show all subjects"""
        # Clear the frame first
        for widget in self.subjects_frame.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.subjects:
            self.no_subjects_label = ttk.Label(
                self.subjects_frame.scrollable_frame, 
                text="No subjects added yet. Click 'Add Subject' to begin."
            )
            self.no_subjects_label.pack(pady=20)
            return
            
        # Add each subject
        for i, subject in enumerate(self.subjects):
            frame = ttk.LabelFrame(
                self.subjects_frame.scrollable_frame,
                text=f"{i+1}. {subject.name} ({subject.credit_hours} credits)"
            )
            frame.pack(fill="x", pady=5, padx=5, anchor="w")
            
            # Components table
            components_text = "Components:\n"
            components_text += f"{'Name':<20} {'Weight':<10} {'My Score':<15} {'Class Avg':<15}\n"
            components_text += "-" * 60 + "\n"
            
            for comp in subject.components:
                components_text += f"{comp.name:<20} {comp.weight:<10.1f}% "
                components_text += f"{comp.my_marks}/{comp.max_marks} "
                components_text += f"{comp.class_avg_marks}/{comp.max_marks}\n"
                
            ttk.Label(frame, text=components_text, justify="left", font=("Courier", 9)).pack(
                anchor="w", padx=10, pady=5)
                
            # Buttons
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(fill="x", pady=5)
            
            ttk.Button(
                btn_frame, text="Edit", 
                command=lambda s=subject, idx=i: self.edit_subject(s, idx)
            ).pack(side="left", padx=5)
            
            ttk.Button(
                btn_frame, text="Delete", 
                command=lambda idx=i: self.delete_subject(idx)
            ).pack(side="left", padx=5)
    
    def add_subject(self):
        """Open dialog to add a new subject"""
        dialog = SubjectDialog(self.parent, on_save=self.save_subject)
        self.wait_window(dialog)
        
    def save_subject(self, subject):
        """Save a subject and update display"""
        self.subjects.append(subject)
        self.update_subjects_display()
        
    def edit_subject(self, subject, index):
        """Open dialog to edit an existing subject"""
        dialog = SubjectDialog(self.parent, subject=subject, on_save=lambda s: self.update_subject(s, index))
        self.wait_window(dialog)
        
    def update_subject(self, subject, index):
        """Update an existing subject"""
        self.subjects[index] = subject
        self.update_subjects_display()
        
    def delete_subject(self, index):
        """Delete a subject"""
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {self.subjects[index].name}?"
        )
        if confirm:
            self.subjects.pop(index)
            self.update_subjects_display()
    
    def save_and_continue(self):
        """Save all data and continue to results screen"""
        if not self.subjects:
            messagebox.showwarning("No Subjects", "Please add at least one subject before calculating results.")
            return
            
        previous_cgpa = None
        previous_credits = None
        
        if self.include_previous_var.get():
            try:
                if self.cgpa_var.get():
                    previous_cgpa = float(self.cgpa_var.get())
                if self.credits_var.get():
                    previous_credits = float(self.credits_var.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers for CGPA and credits.")
                return
        
        semester = Semester(
            "Current Semester",
            self.subjects,
            previous_cgpa,
            previous_credits
        )
        
        self.on_complete(semester)

class SubjectDialog(tk.Toplevel):
    """Dialog for adding/editing a subject"""
    def __init__(self, parent, on_save, subject=None):
        super().__init__(parent)
        self.title("Subject Details")
        self.on_save = on_save
        self.subject = subject
        self.components = []
        
        if subject:
            # Editing existing subject
            self.name_var = tk.StringVar(value=subject.name)
            self.credit_var = tk.StringVar(value=str(subject.credit_hours))
            self.components = list(subject.components)
        else:
            # New subject
            self.name_var = tk.StringVar(value="")
            self.credit_var = tk.StringVar(value="")
        
        self.setup_ui()
        
    def setup_ui(self):
        self.geometry("600x500")
        
        # Title
        ttk.Label(self, text="Subject Details", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Basic information frame
        info_frame = ttk.Frame(self)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        row = ttk.Frame(info_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Subject Name:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.name_var, width=30).pack(side="left", padx=5, fill="x", expand=True)
        
        row = ttk.Frame(info_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Credit Hours:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.credit_var, width=10).pack(side="left", padx=5)
        
        # Components section
        ttk.Label(self, text="Components", font=("TkDefaultFont", 11)).pack(anchor="w", padx=20, pady=5)
        
        # Components list frame
        self.components_frame = ScrollableFrame(self)
        self.components_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Update components display
        self.update_components_display()
        
        # Add component button
        ttk.Button(self, text="Add Component", 
                 command=self.add_component).pack(pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                 command=self.destroy).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Save Subject", 
                 command=self.save_subject).pack(side="right", padx=5)
        
    def update_components_display(self):
        """Update the components list display"""
        # Clear the frame first
        for widget in self.components_frame.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.components:
            ttk.Label(
                self.components_frame.scrollable_frame,
                text="No components added yet. Click 'Add Component' to begin."
            ).pack(pady=20)
            return
            
        # Add table header
        header = ttk.Frame(self.components_frame.scrollable_frame)
        header.pack(fill="x", pady=5)
        ttk.Label(header, text="Component", width=15).grid(row=0, column=0, padx=5)
        ttk.Label(header, text="Weight (%)", width=10).grid(row=0, column=1, padx=5)
        ttk.Label(header, text="Max Marks", width=10).grid(row=0, column=2, padx=5)
        ttk.Label(header, text="My Marks", width=10).grid(row=0, column=3, padx=5)
        ttk.Label(header, text="Class Avg", width=10).grid(row=0, column=4, padx=5)
        ttk.Label(header, text="Actions", width=15).grid(row=0, column=5, padx=5)
        
        # Add each component as a row
        for i, comp in enumerate(self.components):
            row = ttk.Frame(self.components_frame.scrollable_frame)
            row.pack(fill="x", pady=2)
            
            ttk.Label(row, text=comp.name, width=15).grid(row=0, column=0, padx=5)
            ttk.Label(row, text=f"{comp.weight:.1f}", width=10).grid(row=0, column=1, padx=5)
            ttk.Label(row, text=f"{comp.max_marks}", width=10).grid(row=0, column=2, padx=5)
            ttk.Label(row, text=f"{comp.my_marks}", width=10).grid(row=0, column=3, padx=5)
            ttk.Label(row, text=f"{comp.class_avg_marks}", width=10).grid(row=0, column=4, padx=5)
            
            # Action buttons
            btn_frame = ttk.Frame(row)
            btn_frame.grid(row=0, column=5, padx=5)
            
            ttk.Button(
                btn_frame, text="Edit",
                command=lambda c=comp, idx=i: self.edit_component(c, idx)
            ).pack(side="left", padx=2)
            
            ttk.Button(
                btn_frame, text="Delete",
                command=lambda idx=i: self.delete_component(idx)
            ).pack(side="left", padx=2)
            
    def add_component(self):
        """Open dialog to add a new component"""
        dialog = ComponentDialog(self, on_save=self.save_component)
        self.wait_window(dialog)
        
    def save_component(self, component):
        """Save a component and update the display"""
        self.components.append(component)
        self.update_components_display()
        
    def edit_component(self, component, index):
        """Open dialog to edit an existing component"""
        dialog = ComponentDialog(
            self, component=component,
            on_save=lambda c: self.update_component(c, index)
        )
        self.wait_window(dialog)
        
    def update_component(self, component, index):
        """Update an existing component"""
        self.components[index] = component
        self.update_components_display()
        
    def delete_component(self, index):
        """Delete a component"""
        self.components.pop(index)
        self.update_components_display()
        
    def save_subject(self):
        """Save the subject and close dialog"""
        # Validate inputs
        if not self.name_var.get().strip():
            messagebox.showerror("Input Error", "Subject name cannot be empty.")
            return
            
        try:
            credit_hours = float(self.credit_var.get())
            if credit_hours <= 0:
                messagebox.showerror("Input Error", "Credit hours must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for credit hours.")
            return
            
        if not self.components:
            messagebox.showerror("Input Error", "Please add at least one component.")
            return
            
        # Calculate total weight
        total_weight = sum(comp.weight for comp in self.components)
        if total_weight != 100:
            # Normalize weights
            for comp in self.components:
                comp.weight = (comp.weight / total_weight) * 100
            messagebox.showinfo(
                "Weight Normalized",
                f"Component weights have been normalized to total 100% (was {total_weight:.1f}%)."
            )
            
        # Create subject
        subject = Subject(
            self.name_var.get().strip(),
            credit_hours,
            self.components
        )
        
        # Call save callback
        self.on_save(subject)
        self.destroy()

class ComponentDialog(tk.Toplevel):
    """Dialog for adding/editing a component"""
    def __init__(self, parent, on_save, component=None):
        super().__init__(parent)
        self.title("Component Details")
        self.on_save = on_save
        
        if component:
            # Editing existing component
            self.name_var = tk.StringVar(value=component.name)
            self.weight_var = tk.StringVar(value=str(component.weight))
            self.max_marks_var = tk.StringVar(value=str(component.max_marks))
            self.my_marks_var = tk.StringVar(value=str(component.my_marks))
            self.class_avg_var = tk.StringVar(value=str(component.class_avg_marks))
        else:
            # New component
            self.name_var = tk.StringVar(value="")
            self.weight_var = tk.StringVar(value="")
            self.max_marks_var = tk.StringVar(value="")
            self.my_marks_var = tk.StringVar(value="")
            self.class_avg_var = tk.StringVar(value="")
        
        self.setup_ui()
        
    def setup_ui(self):
        self.geometry("400x300")
        
        # Title
        ttk.Label(self, text="Component Details", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Fields frame
        fields_frame = ttk.Frame(self)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Component Name
        row = ttk.Frame(fields_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Component Name:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.name_var, width=25).pack(side="left", padx=5, fill="x", expand=True)
        
        # Weight
        row = ttk.Frame(fields_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Weight (%):", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.weight_var, width=10).pack(side="left", padx=5)
        
        # Max Marks
        row = ttk.Frame(fields_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Maximum Marks:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.max_marks_var, width=10).pack(side="left", padx=5)
        
        # My Marks
        row = ttk.Frame(fields_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="My Marks:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.my_marks_var, width=10).pack(side="left", padx=5)
        
        # Class Average
        row = ttk.Frame(fields_frame)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text="Class Average:", width=15).pack(side="left", padx=5)
        ttk.Entry(row, textvariable=self.class_avg_var, width=10).pack(side="left", padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                 command=self.destroy).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Save", 
                 command=self.save_component).pack(side="right", padx=5)
        
    def save_component(self):
        """Validate and save the component"""
        # Validate inputs
        if not self.name_var.get().strip():
            messagebox.showerror("Input Error", "Component name cannot be empty.")
            return
            
        try:
            weight = float(self.weight_var.get())
            if weight <= 0:
                messagebox.showerror("Input Error", "Weight must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for weight.")
            return
            
        try:
            max_marks = float(self.max_marks_var.get())
            if max_marks <= 0:
                messagebox.showerror("Input Error", "Maximum marks must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for maximum marks.")
            return
            
        try:
            my_marks = float(self.my_marks_var.get())
            if my_marks < 0 or my_marks > max_marks:
                messagebox.showerror("Input Error", f"Your marks must be between 0 and {max_marks}.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for your marks.")
            return
            
        try:
            class_avg = float(self.class_avg_var.get())
            if class_avg < 0 or class_avg > max_marks:
                messagebox.showerror("Input Error", f"Class average must be between 0 and {max_marks}.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for class average.")
            return
            
        # Create component
        component = Component(
            self.name_var.get().strip(),
            weight,
            max_marks,
            my_marks,
            class_avg
        )
        
        # Call save callback
        self.on_save(component)
        self.destroy()

class ResultsScreen(ttk.Frame):
    """Screen for showing calculation results"""
    def __init__(self, parent, semester, grade_scale):
        super().__init__(parent)
        self.parent = parent
        self.semester = semester
        self.grade_scale = grade_scale
        self.semester_summary = generate_semester_summary(semester, grade_scale)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        ttk.Label(self, text="Academic Performance Results", font=("TkDefaultFont", 14, "bold")).pack(pady=10)
        
        # Summary at top
        summary_frame = ttk.LabelFrame(self, text="Semester Summary")
        summary_frame.pack(fill="x", padx=20, pady=5)
        
        sgpa = self.semester_summary["sgpa"]
        ttk.Label(summary_frame, text=f"Semester GPA (SGPA): {sgpa:.2f}", 
                font=("TkDefaultFont", 12)).pack(anchor="w", padx=10, pady=5)
                
        if self.semester_summary["cgpa"] is not None:
            cgpa = self.semester_summary["cgpa"]
            ttk.Label(summary_frame, text=f"Cumulative GPA (CGPA): {cgpa:.2f}", 
                    font=("TkDefaultFont", 12)).pack(anchor="w", padx=10, pady=5)
        
        # Scrollable area for subject details
        subjects_area = ScrollableFrame(self)
        subjects_area.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add each subject
        for subject_summary in self.semester_summary["subjects"]:
            self.add_subject_panel(subjects_area.scrollable_frame, subject_summary)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Save Results", 
                 command=self.save_results).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Start New Analysis", 
                 command=lambda: self.parent.switch_to_start()).pack(side="right", padx=5)
        
    def add_subject_panel(self, parent, subject_summary):
        """Add a collapsible panel for a subject"""
        frame = ttk.LabelFrame(
            parent,
            text=f"{subject_summary['name']} ({subject_summary['credit_hours']} credits) - "
                 f"Grade: {subject_summary['predicted_grade']} ({subject_summary['grade_points']} points)"
        )
        frame.pack(fill="x", pady=5, padx=5)
        
        # Overall stats
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        col1 = ttk.Frame(stats_frame)
        col1.pack(side="left", fill="y", padx=10)
        col2 = ttk.Frame(stats_frame)
        col2.pack(side="left", fill="y", padx=10)
        
        ttk.Label(col1, text=f"My weighted total: {subject_summary['weighted_my_score']:.1f}/100").pack(anchor="w")
        ttk.Label(col1, text=f"Class average: {subject_summary['weighted_class_avg']:.1f}/100").pack(anchor="w")
        
        rel_perf = subject_summary['relative_performance_percentage']
        ttk.Label(col2, text=f"Relative performance: {rel_perf:+.1f}%").pack(anchor="w")
        ttk.Label(col2, text=f"Raw marks: {subject_summary['my_total_raw']}/{subject_summary['max_total_raw']}").pack(anchor="w")
        
        # Components section
        if subject_summary["components"]:
            components_label = ttk.Label(frame, text="Component Breakdown:", font=("TkDefaultFont", 10, "bold"))
            components_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Table headers
            table_frame = ttk.Frame(frame)
            table_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(table_frame, text="Component", width=20, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky="w")
            ttk.Label(table_frame, text="Weight", width=10, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, sticky="w")
            ttk.Label(table_frame, text="My Score", width=15, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky="w")
            ttk.Label(table_frame, text="Class Avg", width=15, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=3, sticky="w")
            ttk.Label(table_frame, text="Relative", width=10, font=("TkDefaultFont", 9, "bold")).grid(row=0, column=4, sticky="w")
            
            # Add separator
            ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=10, pady=5)
            
            # Component rows
            for i, comp in enumerate(subject_summary["components"]):
                row = ttk.Frame(frame)
                row.pack(fill="x", padx=10, pady=2)
                
                ttk.Label(row, text=comp["name"], width=20).grid(row=0, column=0, sticky="w")
                ttk.Label(row, text=f"{comp['weight']:.1f}%", width=10).grid(row=0, column=1, sticky="w")
                ttk.Label(row, text=f"{comp['my_marks']}/{comp['max_marks']} ({comp['my_percentage']:.1f}%)", 
                        width=15).grid(row=0, column=2, sticky="w")
                ttk.Label(row, text=f"{comp['class_avg_marks']}/{comp['max_marks']} ({comp['class_avg_percentage']:.1f}%)", 
                        width=15).grid(row=0, column=3, sticky="w")
                        
                rel_perf = comp['relative_performance_percentage']
                ttk.Label(row, text=f"{rel_perf:+.1f}%", 
                        width=10).grid(row=0, column=4, sticky="w")
    
    def save_results(self):
        """Save results to a JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Results As"
        )
        
        if not file_path:
            return  # User canceled
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.semester_summary, f, indent=2)
            messagebox.showinfo("Save Successful", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")
            
class MainApp(tk.Tk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.title("Academic Performance Tracker")
        self.geometry("800x600")
        
        # Set theme
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass  # If theme is not available, use default
            
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.current_frame = None
        self.switch_to_start()
        
    def switch_to_start(self):
        """Switch to the grade scale customization screen"""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = GradeScaleScreen(
            self.container, 
            on_complete=self.switch_to_subject_entry
        )
        self.current_frame.pack(fill="both", expand=True)
        
    def switch_to_subject_entry(self, grade_scale):
        """Switch to the subject entry screen"""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.grade_scale = grade_scale
        self.current_frame = SubjectEntryScreen(
            self.container, 
            grade_scale,
            on_complete=self.switch_to_results
        )
        self.current_frame.pack(fill="both", expand=True)
        
    def switch_to_results(self, semester):
        """Switch to the results screen"""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = ResultsScreen(
            self.container,
            semester,
            self.grade_scale
        )
        self.current_frame.pack(fill="both", expand=True)

def run_gui():
    """Run the GUI application"""
    app = MainApp()
    app.mainloop()
