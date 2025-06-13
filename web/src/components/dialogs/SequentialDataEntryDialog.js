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
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  VStack,
  HStack,
  Box,
  Text,
  Progress,
  Heading,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast
} from '@chakra-ui/react';
import { Component } from '../../models';

const SequentialDataEntryDialog = ({ isOpen, onClose, onComplete, customizedComponents }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepComponents, setStepComponents] = useState([]);
  const [allSteps, setAllSteps] = useState([]);
  const [finalComponents, setFinalComponents] = useState([]);
  const toast = useToast();

  // Initialize dialog when opened with customized components
  useEffect(() => {
    if (isOpen && customizedComponents && customizedComponents.length > 0) {
      let steps = [];
      
      // Check if this looks like a Standard Academic preset
      const hasQuizzes = customizedComponents.some(comp => comp.name.includes('Quiz'));
      const hasAssignments = customizedComponents.some(comp => comp.name.includes('Assignment'));
      const hasMidSemExam = customizedComponents.some(comp => comp.name.includes('Mid-Semester'));
      const hasEndSemExam = customizedComponents.some(comp => comp.name.includes('End-Semester'));
      
      // If it's the Standard Academic preset, create ordered steps
      if (hasQuizzes && hasAssignments && hasMidSemExam && hasEndSemExam) {
        // Define the priority order for component types
        const componentOrder = ['Quiz', 'Assignment', 'Mid-Semester', 'End-Semester'];
        
        // Group components by their type
        const orderedGroups = {};
        componentOrder.forEach(type => orderedGroups[type] = []);
        
        // Sort each component into its appropriate group
        customizedComponents.forEach(comp => {
          for (const type of componentOrder) {
            if (comp.name.includes(type)) {
              orderedGroups[type].push({
                ...comp,
                maxMarks: comp.maxMarks || (type.includes('Exam') ? 100 : 10),
                myMarks: 0,
                classAvgMarks: 0
              });
              break;
            }
          }
        });
        
        // Create steps in the specified order
        steps = componentOrder
          .filter(type => orderedGroups[type].length > 0)
          .map(type => ({
            name: type,
            components: orderedGroups[type]
          }));
      } else {
        // Fall back to the default grouping for non-standard presets
        const groups = {};
        customizedComponents.forEach(comp => {
          const baseName = comp.name;
          if (!groups[baseName]) {
            groups[baseName] = [];
          }
          groups[baseName].push({...comp});
        });
        
        steps = Object.entries(groups).map(([name, comps]) => ({
          name,
          components: comps.map(c => ({
            ...c,
            maxMarks: c.maxMarks || 10, // Default max marks
            myMarks: 0,
            classAvgMarks: 0
          }))
        }));
      }
      
      // Set the initial state
      setAllSteps(steps);
      setStepComponents(steps[0]?.components || []);
      setCurrentStep(0);
      setFinalComponents([]);
    }
  }, [isOpen, customizedComponents]);

  // Add a helper function to get better step titles
  const getStepTitle = (stepName) => {
    if (stepName === 'Quiz') return 'Quizzes';
    if (stepName === 'Assignment') return 'Assignments';
    if (stepName === 'Mid-Semester') return 'Mid-Semester Exam';
    if (stepName === 'End-Semester') return 'End-Semester Exam';
    return stepName;
  };

  const handleMaxMarksChange = (value, index) => {
    const newComponents = [...stepComponents];
    newComponents[index].maxMarks = Number(value);
    setStepComponents(newComponents);
  };

  const handleMyMarksChange = (value, index) => {
    const newComponents = [...stepComponents];
    newComponents[index].myMarks = Number(value);
    setStepComponents(newComponents);
  };

  const handleClassAvgChange = (value, index) => {
    const newComponents = [...stepComponents];
    newComponents[index].classAvgMarks = Number(value);
    setStepComponents(newComponents);
  };

  const applyMaxMarksToAll = (value) => {
    const newComponents = stepComponents.map(comp => ({
      ...comp,
      maxMarks: Number(value)
    }));
    setStepComponents(newComponents);
  };

  const applyClassAvgToAll = (value) => {
    const newComponents = stepComponents.map(comp => ({
      ...comp,
      classAvgMarks: Number(value)
    }));
    setStepComponents(newComponents);
  };

  const nextStep = () => {
    // Validate current step
    for (let i = 0; i < stepComponents.length; i++) {
      const comp = stepComponents[i];
      
      if (comp.maxMarks <= 0) {
        toast({
          title: "Invalid max marks",
          description: `Max marks for ${comp.name} must be greater than zero.`,
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      if (comp.myMarks < 0 || comp.myMarks > comp.maxMarks) {
        toast({
          title: "Invalid marks",
          description: `Your marks for ${comp.name} must be between 0 and ${comp.maxMarks}.`,
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      if (comp.classAvgMarks < 0 || comp.classAvgMarks > comp.maxMarks) {
        toast({
          title: "Invalid class average",
          description: `Class average for ${comp.name} must be between 0 and ${comp.maxMarks}.`,
          status: "error",
          duration: 3000,
          isClosable: true,
        });
        return;
      }
    }
    
    // Save current step components
    const updatedFinalComponents = [...finalComponents, ...stepComponents];
    setFinalComponents(updatedFinalComponents);
    
    // Move to next step or finish
    if (currentStep < allSteps.length - 1) {
      const nextStepIndex = currentStep + 1;
      setCurrentStep(nextStepIndex);
      setStepComponents(allSteps[nextStepIndex].components);
    } else {
      // Create and return final components
      try {
        const finalComponentsList = updatedFinalComponents.map(comp => {
          // Ensure all required fields have valid values
          const maxMarks = Number(comp.maxMarks) || 1; // Prevent division by zero
          const myMarks = Number(comp.myMarks) || 0;
          const classAvgMarks = Number(comp.classAvgMarks) || 0;
          const weight = Number(comp.weight) || 0;
          
          // Create a proper Component instance with all required fields
          return new Component(
            comp.name,
            weight,
            maxMarks,
            myMarks,
            classAvgMarks
          );
        });
        
        // Make sure we have at least one valid component
        if (finalComponentsList.length === 0) {
          toast({
            title: "No components to add",
            description: "Please add at least one component with valid data.",
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }
        
        // Pass the properly formed components to the callback
        onComplete(finalComponentsList);
      } catch (error) {
        console.error("Error creating components:", error);
        toast({
          title: "Error creating components",
          description: "There was an error processing your data. Please try again.",
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const progressPercent = allSteps.length > 0 
    ? ((currentStep + 1) / allSteps.length) * 100 
    : 0;

  // For distribution components like quizzes, enable "Apply to all" option
  const isGroupComponent = stepComponents.length > 1;
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" closeOnOverlayClick={false}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <Text>Enter Component Details</Text>
          <Progress 
            value={progressPercent} 
            size="sm" 
            colorScheme="teal" 
            mt={2} 
            borderRadius="md" 
          />
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Heading size="md">
              {getStepTitle(allSteps[currentStep]?.name) || 'Component'} Details
              <Text fontSize="sm" fontWeight="normal" mt={1}>
                Step {currentStep + 1} of {allSteps.length}
              </Text>
            </Heading>
            
            <Divider />
            
            {/* Show different instructions based on component type */}
            {allSteps[currentStep]?.name === 'Mid-Semester' && (
              <Box bg="blue.50" p={3} borderRadius="md">
                <Text fontWeight="bold">Mid-Semester Exam</Text>
                <Text fontSize="sm">Enter the details for your mid-semester exam.</Text>
              </Box>
            )}
            
            {allSteps[currentStep]?.name === 'End-Semester' && (
              <Box bg="purple.50" p={3} borderRadius="md">
                <Text fontWeight="bold">End-Semester Exam</Text>
                <Text fontSize="sm">Enter the details for your final end-semester exam.</Text>
              </Box>
            )}
            
            {isGroupComponent && (
              <Box bg="gray.50" p={3} borderRadius="md">
                <Text fontWeight="bold" mb={2}>
                  Quick Set Max Marks for All {getStepTitle(allSteps[currentStep]?.name)}
                </Text>
                <FormControl>
                  <FormLabel fontSize="sm">Max Marks</FormLabel>
                  <NumberInput size="sm" min={0}>
                    <NumberInputField 
                      placeholder={allSteps[currentStep]?.name.includes('Exam') ? "e.g., 100" : "e.g., 10"} 
                      onBlur={(e) => applyMaxMarksToAll(e.target.value)} 
                    />
                  </NumberInput>
                </FormControl>
              </Box>
            )}
            
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Component</Th>
                  <Th>Weight</Th>
                  <Th>Max Marks</Th>
                  <Th>My Marks</Th>
                  <Th>Class Avg</Th>
                </Tr>
              </Thead>
              <Tbody>
                {stepComponents.map((comp, idx) => (
                  <Tr key={idx}>
                    <Td>{comp.name}</Td>
                    <Td>{comp.weight.toFixed(1)}%</Td>
                    <Td>
                      <NumberInput 
                        size="sm" 
                        min={1} 
                        value={comp.maxMarks}
                        onChange={(value) => handleMaxMarksChange(value, idx)}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </Td>
                    <Td>
                      <NumberInput 
                        size="sm" 
                        min={0} 
                        max={comp.maxMarks}
                        value={comp.myMarks}
                        onChange={(value) => handleMyMarksChange(value, idx)}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </Td>
                    <Td>
                      <NumberInput 
                        size="sm" 
                        min={0} 
                        max={comp.maxMarks}
                        value={comp.classAvgMarks}
                        onChange={(value) => handleClassAvgChange(value, idx)}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </VStack>
        </ModalBody>
        
        <ModalFooter>
          <Button colorScheme="gray" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="teal" onClick={nextStep}>
            {currentStep < allSteps.length - 1 ? 'Next' : 'Finish'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
export default SequentialDataEntryDialog;
