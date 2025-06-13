import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack
} from '@chakra-ui/react';
import { Component } from '../../models';

const ComponentDialog = ({ isOpen, onClose, onSave, component = null }) => {
  const [name, setName] = useState('');
  const [weight, setWeight] = useState('');
  const [maxMarks, setMaxMarks] = useState('');
  const [myMarks, setMyMarks] = useState('');
  const [classAvgMarks, setClassAvgMarks] = useState('');

  // Initialize the form when the dialog is opened or a component is provided for editing
  useEffect(() => {
    if (isOpen) {
      if (component) {
        // Editing existing component
        setName(component.name);
        setWeight(component.weight.toString());
        setMaxMarks(component.maxMarks.toString());
        setMyMarks(component.myMarks.toString());
        setClassAvgMarks(component.classAvgMarks.toString());
      } else {
        // New component
        setName('');
        setWeight('');
        setMaxMarks('');
        setMyMarks('');
        setClassAvgMarks('');
      }
    }
  }, [isOpen, component]);

  const handleSave = () => {
    // Validate inputs
    if (!name.trim()) {
      alert("Component name cannot be empty.");
      return;
    }
    
    try {
      const weightVal = parseFloat(weight);
      if (weightVal <= 0) {
        alert("Weight must be greater than zero.");
        return;
      }
      
      const maxMarksVal = parseFloat(maxMarks);
      if (maxMarksVal <= 0) {
        alert("Maximum marks must be greater than zero.");
        return;
      }
      
      const myMarksVal = parseFloat(myMarks);
      if (myMarksVal < 0 || myMarksVal > maxMarksVal) {
        alert(`Your marks must be between 0 and ${maxMarksVal}.`);
        return;
      }
      
      const classAvgVal = parseFloat(classAvgMarks);
      if (classAvgVal < 0 || classAvgVal > maxMarksVal) {
        alert(`Class average must be between 0 and ${maxMarksVal}.`);
        return;
      }
      
      // Create component
      const newComponent = new Component(
        name.trim(),
        weightVal,
        maxMarksVal,
        myMarksVal,
        classAvgVal
      );
      
      onSave(newComponent);
    } catch (error) {
      alert("Please enter valid numbers for all fields.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{component ? 'Edit Component' : 'Add Component'}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4}>
            <FormControl isRequired>
              <FormLabel>Component Name</FormLabel>
              <Input 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="e.g., Midterm Exam"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Weight (%)</FormLabel>
              <Input 
                type="number" 
                value={weight} 
                onChange={(e) => setWeight(e.target.value)} 
                placeholder="e.g., 20"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Maximum Marks</FormLabel>
              <Input 
                type="number" 
                value={maxMarks} 
                onChange={(e) => setMaxMarks(e.target.value)} 
                placeholder="e.g., 100"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>My Marks</FormLabel>
              <Input 
                type="number" 
                value={myMarks} 
                onChange={(e) => setMyMarks(e.target.value)} 
                placeholder="e.g., 85"
              />
            </FormControl>
            
            <FormControl isRequired>
              <FormLabel>Class Average Marks</FormLabel>
              <Input 
                type="number" 
                value={classAvgMarks} 
                onChange={(e) => setClassAvgMarks(e.target.value)} 
                placeholder="e.g., 75"
              />
            </FormControl>
          </VStack>
        </ModalBody>
        
        <ModalFooter>
          <Button colorScheme="gray" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="teal" onClick={handleSave}>
            Save
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ComponentDialog;
