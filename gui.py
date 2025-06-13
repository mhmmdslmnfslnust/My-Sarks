import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, List, Optional, Tuple

from models import Component, Subject, Semester, GradeScale
from calculator import create_default_grade_scale, generate_semester_summary

# Define common presets
SUBJECT_PRESETS = {
    "Standard Academic": [
        {"name": "Quizzes", "weight": 10, "count": 4, "is_group": True},
        {"name": "Assignments", "weight": 10, "count": 2, "is_group": True},
        {"name": "Mid-Semester Exam", "weight": 30, "count": 1, "is_group": False},
        {"name": "End-Semester Exam", "weight": 50, "count": 1, "is_group": False},
    ],
    "Lab Course": [
        {"name": "Lab Reports", "weight": 30, "count": 8, "is_group": True},
        {"name": "Lab Performance", "weight": 30, "count": 1, "is_group": False},
        {"name": "Lab Project", "weight": 20, "count": 1, "is_group": False},
        {"name": "Lab Exam", "weight": 20, "count": 1, "is_group": False},
    ],
    "Project Based": [
        {"name": "Progress Reports", "weight": 20, "count": 3, "is_group": True},
        {"name": "Presentations", "weight": 30, "count": 2, "is_group": True},
        {"name": "Final Project", "weight": 40, "count": 1, "is_group": False},
        {"name": "Peer Review", "weight": 10, "count": 1, "is_group": False},
    ],
    "Custom": []  # Empty preset for manual entry
}

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
        self.include_lab = tk.BooleanVar(value=False)
        self.lab_credits = tk.StringVar(value="0")
        self.theory_credits = tk.StringVar(value="0")
        self.selected_preset = tk.StringVar(value="Custom")
        
        if subject:
            # Editing existing subject
            self.name_var = tk.StringVar(value=subject.name)
            self.credit_var = tk.StringVar(value=str(subject.credit_hours))
            self.components = list(subject.components)
            
            # Try to detect if this has lab components
            if "Lab" in subject.name or any("Lab" in comp.name for comp in subject.components):
                self.include_lab.set(True)
        else:
            # New subject
            self.name_var = tk.StringVar(value="")
            self.credit_var = tk.StringVar(value="")
        
        self.setup_ui()
        
        # Make sure the dialog is modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
    def setup_ui(self):
        self.geometry("650x600")
        
        # Title
        ttk.Label(self, text="Subject Details", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Basic information frame
        info_frame = ttk.LabelFrame(self, text="Basic Information")
        info_frame.pack(fill="x", padx=20, pady=10)
        
        row = ttk.Frame(info_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text="Subject Name:", width=15).pack(side="left")
        ttk.Entry(row, textvariable=self.name_var, width=30).pack(side="left", padx=5, fill="x", expand=True)
        
        # Credit hours section with lab option
        credit_frame = ttk.Frame(info_frame)
        credit_frame.pack(fill="x", pady=5, padx=10)
        
        # Standard credit hours
        credit_row = ttk.Frame(credit_frame)
        credit_row.pack(fill="x", pady=5)
        
        ttk.Label(credit_row, text="Credit Hours:", width=15).pack(side="left")
        ttk.Entry(credit_row, textvariable=self.credit_var, width=10).pack(side="left", padx=5)
        
        # Lab option
        lab_check = ttk.Checkbutton(
            credit_frame, text="Subject includes lab component", 
            variable=self.include_lab, command=self.toggle_lab_view
        )
        lab_check.pack(anchor="w", pady=5)
        
        # Lab credit frame (initially hidden)
        self.lab_credit_frame = ttk.Frame(credit_frame)
        
        ttk.Label(self.lab_credit_frame, text="Theory Credits:").pack(side="left", padx=5)
        ttk.Entry(self.lab_credit_frame, textvariable=self.theory_credits, width=5).pack(side="left", padx=5)
        
        ttk.Label(self.lab_credit_frame, text="Lab Credits:").pack(side="left", padx=5)
        ttk.Entry(self.lab_credit_frame, textvariable=self.lab_credits, width=5).pack(side="left", padx=5)
        
        # Component preset section
        preset_frame = ttk.LabelFrame(self, text="Component Presets")
        preset_frame.pack(fill="x", padx=20, pady=10)
        
        preset_row = ttk.Frame(preset_frame)
        preset_row.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(preset_row, text="Select a preset:").pack(side="left", padx=5)
        preset_dropdown = ttk.Combobox(
            preset_row, textvariable=self.selected_preset,
            values=list(SUBJECT_PRESETS.keys()),
            width=20, state="readonly"
        )
        preset_dropdown.pack(side="left", padx=5)
        preset_dropdown.bind("<<ComboboxSelected>>", self.preset_selected)
        
        ttk.Button(preset_row, text="Apply Preset", command=self.apply_preset).pack(side="left", padx=10)
        
        # Components section
        components_label = ttk.Label(self, text="Components", font=("TkDefaultFont", 11))
        components_label.pack(anchor="w", padx=20, pady=5)
        
        # Components list frame
        self.components_frame = ScrollableFrame(self)
        self.components_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Update components display
        self.update_components_display()
        
        # Component management buttons
        btn_row = ttk.Frame(self)
        btn_row.pack(fill="x", padx=20, pady=5)
        
        ttk.Button(btn_row, text="Add Single Component", 
                 command=self.add_single_component).pack(side="left", padx=5)
                 
        ttk.Button(btn_row, text="Add Multiple Quizzes", 
                 command=lambda: self.add_multiple_components("Quiz")).pack(side="left", padx=5)
                 
        ttk.Button(btn_row, text="Add Multiple Assignments", 
                 command=lambda: self.add_multiple_components("Assignment")).pack(side="left", padx=5)
        
        # Bottom buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                 command=self.destroy).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Save Subject", 
                 command=self.save_subject).pack(side="right", padx=5)
        
        # Initialize lab visibility
        self.toggle_lab_view()
        
    def toggle_lab_view(self):
        """Toggle visibility of lab credit fields"""
        if self.include_lab.get():
            self.lab_credit_frame.pack(fill="x", pady=5)
            # If main credit is already set, distribute it between theory and lab
            if self.credit_var.get().strip():
                try:
                    total = float(self.credit_var.get())
                    theory = total * 0.7  # Default distribution: 70% theory, 30% lab
                    lab = total * 0.3
                    self.theory_credits.set(f"{theory:.1f}")
                    self.lab_credits.set(f"{lab:.1f}")
                except ValueError:
                    pass
        else:
            self.lab_credit_frame.pack_forget()
    
    def preset_selected(self, event=None):
        """Handle preset selection"""
        # Just update the UI to show the selected preset description
        preset_name = self.selected_preset.get()
        
        # You could show a description of the preset here if desired
        if preset_name != "Custom" and preset_name in SUBJECT_PRESETS:
            components = SUBJECT_PRESETS[preset_name]
            component_desc = ", ".join([f"{c['name']} ({c['weight']}%)" for c in components])
            # Could display this description somewhere if desired
    
    def apply_preset(self):
        """Apply the selected component preset"""
        preset_name = self.selected_preset.get()
        
        if preset_name == "Custom":
            messagebox.showinfo("Custom Selected", "No preset applied. Add components manually.")
            return
            
        if preset_name not in SUBJECT_PRESETS:
            return
            
        # Confirm if there are existing components
        if self.components and not messagebox.askyesno(
            "Clear Existing Components?",
            "Applying a preset will replace all existing components. Continue?"
        ):
            return
            
        # Clear current components
        self.components = []
        
        # Get preset components
        preset_components = SUBJECT_PRESETS[preset_name]
        
        # Process each preset component
        for preset_comp in preset_components:
            if preset_comp["is_group"] and preset_comp["count"] > 1:
                # For group components like multiple quizzes
                self.add_multiple_components_from_preset(
                    preset_comp["name"], 
                    preset_comp["count"],
                    preset_comp["weight"]
                )
            else:
                # Single component
                self.add_single_component_from_preset(
                    preset_comp["name"],
                    preset_comp["weight"]
                )
                
        # Update the display
        self.update_components_display()
    
    def add_multiple_components_from_preset(self, base_name, count, total_weight):
        """Add multiple similar components from a preset"""
        # We'll open a dialog to get details for all items at once
        dialog = MultiComponentDialog(
            self, base_name, count, total_weight,
            on_save=self.save_multiple_components
        )
        dialog.grab_set()  # Make dialog modal
        self.wait_window(dialog)
    
    def add_single_component_from_preset(self, name, weight):
        """Add a single component from a preset"""
        # Create a placeholder component - user will edit details later
        new_component = Component(
            name=name,
            weight=weight,
            max_marks=100.0,  # Default
            my_marks=0.0,     # Default
            class_avg_marks=0.0  # Default
        )
        self.components.append(new_component)
    
    def update_components_display(self):
        """Update the components list display"""
        # Clear the frame first
        for widget in self.components_frame.scrollable_frame.winfo_children():
            widget.destroy()
            
        if not self.components:
            ttk.Label(
                self.components_frame.scrollable_frame,
                text="No components added yet. Use the buttons below to add components."
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
            
            # Fix: Create a function that has the component index hardcoded
            def create_edit_func(index):
                return lambda: self.edit_component(self.components[index], index)
            
            # Fix: Create a function that has the component index hardcoded
            def create_delete_func(index):
                return lambda: self.delete_component(index)
            
            ttk.Button(
                btn_frame, text="Edit",
                command=create_edit_func(i)
            ).pack(side="left", padx=2)
            
            ttk.Button(
                btn_frame, text="Delete",
                command=create_delete_func(i)
            ).pack(side="left", padx=2)
    
    def add_single_component(self):
        """Open dialog to add a new component"""
        dialog = ComponentDialog(self, on_save=self.save_component)
        dialog.grab_set()  # Make dialog modal
        self.wait_window(dialog)
    
    def add_multiple_components(self, base_name):
        """Open dialog to add multiple similar components at once"""
        dialog = MultiComponentDialog(
            self, base_name, 4, 10.0,  # Default 4 components with 10% weight
            on_save=self.save_multiple_components
        )
        dialog.grab_set()  # Make dialog modal
        self.wait_window(dialog)
        
    def save_component(self, component):
        """Save a component and update the display"""
        self.components.append(component)
        self.update_components_display()
    
    def save_multiple_components(self, components):
        """Save multiple components and update the display"""
        self.components.extend(components)
        self.update_components_display()
        
    def edit_component(self, component, index):
        """Open dialog to edit an existing component"""
        # Fix: Make a copy of the component to avoid reference issues
        dialog = ComponentDialog(
            self, 
            component=component,
            on_save=lambda c: self.update_component(c, index)
        )
        dialog.grab_set()  # Make dialog modal
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
        
        # Get credit hours based on whether lab component is included
        try:
            if self.include_lab.get():
                theory_credits = float(self.theory_credits.get())
                lab_credits = float(self.lab_credits.get())
                credit_hours = theory_credits + lab_credits
            else:
                credit_hours = float(self.credit_var.get())
                
            if credit_hours <= 0:
                messagebox.showerror("Input Error", "Credit hours must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for credit hours.")
            return
            
        if not self.components:
            messagebox.showerror("Input Error", "Please add at least one component.")
            return
            
        # Calculate total weight
        total_weight = sum(comp.weight for comp in self.components)
        if abs(total_weight - 100) > 0.01:  # Allow tiny rounding errors
            # Normalize weights
            normalize = messagebox.askyesno(
                "Weight Normalization",
                f"Component weights total {total_weight:.1f}% instead of 100%. Normalize automatically?"
            )
            if normalize:
                for comp in self.components:
                    comp.weight = (comp.weight / total_weight) * 100
            else:
                messagebox.showerror("Input Error", "Component weights must total 100%.")
                return
            
        # Create subject
        subject_name = self.name_var.get().strip()
        if self.include_lab.get():
            subject_name += f" (Theory: {self.theory_credits.get()}, Lab: {self.lab_credits.get()})"
            
        subject = Subject(
            subject_name,
            credit_hours,
            self.components
        )
        
        # Call save callback
        self.on_save(subject)
        self.destroy()

class MultiComponentDialog(tk.Toplevel):
    """Dialog for adding multiple similar components at once"""
    def __init__(self, parent, base_name, count, total_weight, on_save):
        super().__init__(parent)
        self.title(f"Add Multiple {base_name}s")
        self.parent = parent
        self.on_save = on_save
        self.base_name = base_name
        
        # Variables
        self.count_var = tk.StringVar(value=str(count))
        self.weight_var = tk.StringVar(value=str(total_weight))
        self.distribution_method = tk.StringVar(value="equal")  # "equal" or "by_marks"
        
        # Component data
        self.max_marks_vars = []
        self.my_marks_vars = []
        self.class_avg_vars = []
        
        # Make the dialog modal
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.geometry("650x500")
        
        # Title
        ttk.Label(self, text=f"Add Multiple {self.base_name}s", font=("TkDefaultFont", 12, "bold")).pack(pady=10)
        
        # Count and weight settings
        settings_frame = ttk.LabelFrame(self, text="Settings")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        row = ttk.Frame(settings_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text=f"Number of {self.base_name}s:").pack(side="left", padx=5)
        count_entry = ttk.Entry(row, textvariable=self.count_var, width=5)
        count_entry.pack(side="left", padx=5)
        
        row = ttk.Frame(settings_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text=f"Total weight for all {self.base_name}s (%):").pack(side="left", padx=5)
        weight_entry = ttk.Entry(row, textvariable=self.weight_var, width=5)
        weight_entry.pack(side="left", padx=5)
        
        # Weight distribution method
        row = ttk.Frame(settings_frame)
        row.pack(fill="x", pady=5, padx=10)
        ttk.Label(row, text="Weight distribution method:").pack(side="left", padx=5)
        
        ttk.Radiobutton(
            row, text="Equal weight for each",
            variable=self.distribution_method, value="equal"
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            row, text="Weighted by max marks",
            variable=self.distribution_method, value="by_marks"
        ).pack(side="left", padx=5)
        
        # Apply button
        ttk.Button(settings_frame, text="Generate Component Fields", 
                  command=self.generate_component_fields).pack(pady=10)
        
        # Scrollable area for component entries
        self.component_area = ScrollableFrame(self)
        self.component_area.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial generation
        self.generate_component_fields()
        
        # Bottom buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                  command=self.destroy).pack(side="left", padx=5)
                  
        ttk.Button(btn_frame, text="Save All Components", 
                  command=self.save_components).pack(side="right", padx=5)
    
    def generate_component_fields(self):
        """Generate input fields for each component based on count"""
        try:
            count = int(self.count_var.get())
            if count <= 0:
                messagebox.showerror("Input Error", "Count must be at least 1.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number for count.")
            return
            
        # Clear existing fields
        for widget in self.component_area.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.max_marks_vars = []
        self.my_marks_vars = []
        self.class_avg_vars = []
        
        # Add header
        header = ttk.Frame(self.component_area.scrollable_frame)
        header.pack(fill="x", pady=5)
        ttk.Label(header, text=f"{self.base_name} #", width=10).grid(row=0, column=0, padx=5)
        ttk.Label(header, text="Max Marks", width=10).grid(row=0, column=1, padx=5)
        ttk.Label(header, text="My Marks", width=10).grid(row=0, column=2, padx=5)
        ttk.Label(header, text="Class Average", width=15).grid(row=0, column=3, padx=5)
        
        # Add fields for each component
        for i in range(count):
            row = ttk.Frame(self.component_area.scrollable_frame)
            row.pack(fill="x", pady=2)
            
            ttk.Label(row, text=f"{self.base_name} {i+1}", width=10).grid(row=0, column=0, padx=5)
            
            max_var = tk.StringVar(value="10")  # Default max marks
            max_entry = ttk.Entry(row, textvariable=max_var, width=10)
            max_entry.grid(row=0, column=1, padx=5)
            self.max_marks_vars.append(max_var)
            
            my_var = tk.StringVar(value="0")
            my_entry = ttk.Entry(row, textvariable=my_var, width=10)
            my_entry.grid(row=0, column=2, padx=5)
            self.my_marks_vars.append(my_var)
            
            avg_var = tk.StringVar(value="0")
            avg_entry = ttk.Entry(row, textvariable=avg_var, width=10)
            avg_entry.grid(row=0, column=3, padx=5)
            self.class_avg_vars.append(avg_var)
    
    def save_components(self):
        """Create and save all components"""
        try:
            count = int(self.count_var.get())
            total_weight = float(self.weight_var.get())
            
            if count <= 0:
                messagebox.showerror("Input Error", "Count must be at least 1.")
                return
                
            if total_weight <= 0:
                messagebox.showerror("Input Error", "Total weight must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for count and weight.")
            return
            
        # Parse all component data
        max_marks_list = []
        my_marks_list = []
        class_avg_list = []
        
        try:
            for i in range(count):
                max_marks_list.append(float(self.max_marks_vars[i].get()))
                my_marks_list.append(float(self.my_marks_vars[i].get()))
                class_avg_list.append(float(self.class_avg_vars[i].get()))
                
                # Validate
                if max_marks_list[-1] <= 0:
                    messagebox.showerror("Input Error", f"Max marks for {self.base_name} {i+1} must be greater than zero.")
                    return
                    
                if my_marks_list[-1] < 0 or my_marks_list[-1] > max_marks_list[-1]:
                    messagebox.showerror("Input Error", f"My marks for {self.base_name} {i+1} must be between 0 and {max_marks_list[-1]}.")
                    return
                    
                if class_avg_list[-1] < 0 or class_avg_list[-1] > max_marks_list[-1]:
                    messagebox.showerror("Input Error", f"Class average for {self.base_name} {i+1} must be between 0 and {max_marks_list[-1]}.")
                    return
        except IndexError:
            messagebox.showerror("Input Error", "Missing input fields. Try regenerating the component fields.")
            return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")
            return
            
        # Calculate individual weights based on distribution method
        individual_weights = []
        
        if self.distribution_method.get() == "equal":
            # Equal weight distribution
            weight_per_item = total_weight / count
            individual_weights = [weight_per_item] * count
        else:
            # Weighted by max marks
            total_max_marks = sum(max_marks_list)
            if total_max_marks > 0:
                for max_mark in max_marks_list:
                    weight = (max_mark / total_max_marks) * total_weight
                    individual_weights.append(weight)
            else:
                # Fallback to equal distribution
                weight_per_item = total_weight / count
                individual_weights = [weight_per_item] * count
        
        # Create components
        components = []
        for i in range(count):
            component = Component(
                name=f"{self.base_name} {i+1}",
                weight=individual_weights[i],
                max_marks=max_marks_list[i],
                my_marks=my_marks_list[i],
                class_avg_marks=class_avg_list[i]
            )
            components.append(component)
            
        # Call save callback
        self.on_save(components)
        self.destroy()

class ComponentDialog(tk.Toplevel):
    """Dialog for adding/editing a component"""
    def __init__(self, parent, on_save, component=None):
        super().__init__(parent)
        self.title("Component Details")
        self.on_save = on_save
        
        if component:
            # Editing existing component - make a copy to avoid reference issues
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
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
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
