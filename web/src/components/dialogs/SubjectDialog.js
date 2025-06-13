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
  Select,
  Checkbox,
  VStack,
  HStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  IconButton,
  useDisclosure,
  Flex,
  Badge,
  Box,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { Subject, Component } from '../../models';
import { SUBJECT_PRESETS } from '../../utils/calculator';
import ComponentDialog from './ComponentDialog';
import MultiComponentDialog from './MultiComponentDialog';
import PresetCustomizationDialog from './PresetCustomizationDialog';
import SequentialDataEntryDialog from './SequentialDataEntryDialog';

// Main component
const SubjectDialog = ({ isOpen, onClose, onSave, subject = null }) => {
  const [name, setName] = useState('');
  const [creditHours, setCreditHours] = useState('');
  const [components, setComponents] = useState([]);
  const [includeLab, setIncludeLab] = useState(false);
  const [theoryCredits, setTheoryCredits] = useState('0');
  const [labCredits, setLabCredits] = useState('0');
  const [selectedPreset, setSelectedPreset] = useState('Custom');
  const [totalWeight, setTotalWeight] = useState(0);
  
  // Dialog state
  const componentDialog = useDisclosure();
  const multiComponentDialog = useDisclosure();
  const presetCustomizationDialog = useDisclosure();
  const sequentialDataEntryDialog = useDisclosure();
  
  // Current editing state
  const [currentComponent, setCurrentComponent] = useState(null);
  const [editIndex, setEditIndex] = useState(null);
  const [multiComponentParams, setMultiComponentParams] = useState({
    baseName: '',
    count: 4,
    totalWeight: 10
  });
  const [presetToCustomize, setPresetToCustomize] = useState(null);
  const [componentsToEnterData, setComponentsToEnterData] = useState([]);

  // Initialize form when dialog is opened
  useEffect(() => {
    if (isOpen) {
      if (subject) {
        // Editing existing subject
        setName(subject.name);
        setCreditHours(subject.creditHours.toString());
        setComponents([...subject.components]);
        
        // Try to detect if this has lab components
        if (subject.name.includes('Lab') || subject.components.some(comp => comp.name.includes('Lab'))) {
          setIncludeLab(true);
          // Default distribution: 70% theory, 30% lab
          setTheoryCredits((subject.creditHours * 0.7).toFixed(1));
          setLabCredits((subject.creditHours * 0.3).toFixed(1));
        }
      } else {
        // New subject
        setName('');
        setCreditHours('');
        setComponents([]);
        setIncludeLab(false);
        setTheoryCredits('0');
        setLabCredits('0');
        setSelectedPreset('Custom');
      }
      
      // Calculate total weight
      updateTotalWeight();
    }
  }, [isOpen, subject]);
  
  // Update total weight whenever components change
  useEffect(() => {
    updateTotalWeight();
  }, [components]);
  
  const updateTotalWeight = () => {
    const total = components.reduce((sum, comp) => sum + comp.weight, 0);
    setTotalWeight(total);
  };

  // Event handlers
  const handleSave = () => {
    // Validate inputs
    if (!name.trim()) {
      alert("Subject name cannot be empty.");
      return;
    }
    
    // Get credit hours based on whether lab component is included
    let credits;
    try {
      if (includeLab) {
        const theory = parseFloat(theoryCredits);
        const lab = parseFloat(labCredits);
        credits = theory + lab;
      } else {
        credits = parseFloat(creditHours);
      }
      
      if (credits <= 0) {
        alert("Credit hours must be greater than zero.");
        return;
      }
    } catch (error) {
      alert("Please enter valid numbers for credit hours.");
      return;
    }
    
    if (components.length === 0) {
      alert("Please add at least one component.");
      return;
    }
    
    // Calculate total weight
    if (Math.abs(totalWeight - 100) > 0.01) {  // Allow tiny rounding errors
      // Normalize weights
      const normalize = window.confirm(
        `Component weights total ${totalWeight.toFixed(1)}% instead of 100%. Normalize automatically?`
      );
      if (normalize) {
        const normalizedComponents = components.map(comp => ({
          ...comp,
          weight: (comp.weight / totalWeight) * 100
        }));
        setComponents(normalizedComponents);
      } else {
        alert("Component weights must total 100%.");
        return;
      }
    }
    
    // Create subject
    let subjectName = name.trim();
    if (includeLab) {
      subjectName += ` (Theory: ${theoryCredits}, Lab: ${labCredits})`;
    }
    
    const newSubject = new Subject(subjectName, credits, components);
    onSave(newSubject);
  };

  const handleAddComponent = () => {
    setCurrentComponent(null);
    setEditIndex(null);
    componentDialog.onOpen();
  };

  const handleEditComponent = (component, index) => {
    setCurrentComponent({...component});
    setEditIndex(index);
    componentDialog.onOpen();
  };

  const handleDeleteComponent = (index) => {
    if (window.confirm('Are you sure you want to delete this component?')) {
      const newComponents = [...components];
      newComponents.splice(index, 1);
      setComponents(newComponents);
    }
  };

  const handleSaveComponent = (component) => {
    if (editIndex !== null) {
      const newComponents = [...components];
      newComponents[editIndex] = component;
      setComponents(newComponents);
    } else {
      setComponents([...components, component]);
    }
    componentDialog.onClose();
  };

  const handleAddMultipleComponents = (baseName) => {
    setMultiComponentParams({
      baseName,
      count: 4,
      totalWeight: 10
    });
    multiComponentDialog.onOpen();
  };

  const handleSaveMultipleComponents = (newComponents) => {
    setComponents([...components, ...newComponents]);
    multiComponentDialog.onClose();
  };

  const handleApplyPreset = () => {
    if (selectedPreset === 'Custom') {
      alert("No preset applied. Add components manually.");
      return;
    }
    
    // Confirm if there are existing components
    if (components.length > 0) {
      if (!window.confirm("Applying a preset will replace all existing components. Continue?")) {
        return;
      }
    }
    
    // Open customization dialog with the selected preset
    const presetComponents = SUBJECT_PRESETS[selectedPreset];
    setPresetToCustomize([...presetComponents]);
    presetCustomizationDialog.onOpen();
  };
  
  const handleApplyCustomizedPreset = (customizedComponents) => {
    // Start sequential data entry for the customized components
    setComponentsToEnterData(customizedComponents);
    sequentialDataEntryDialog.onOpen();
  };

  const handleSequentialDataEntryComplete = (finalComponents) => {
    // Set the components with all data entered
    setComponents(finalComponents);
    sequentialDataEntryDialog.onClose();
  };

  return (
    <React.Fragment>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{subject ? 'Edit Subject' : 'Add Subject'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Tabs>
              <TabList>
                <Tab>Basic Info</Tab>
                <Tab>Components</Tab>
                <Tab>Presets</Tab>
              </TabList>
              
              <TabPanels>
                {/* Basic Information Tab */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <FormControl isRequired>
                      <FormLabel>Subject Name</FormLabel>
                      <Input 
                        value={name} 
                        onChange={(e) => setName(e.target.value)} 
                        placeholder="e.g., Mathematics 101"
                      />
                    </FormControl>
                    
                    <FormControl isRequired>
                      <FormLabel>Credit Hours</FormLabel>
                      <Input 
                        type="number" 
                        value={creditHours} 
                        onChange={(e) => setCreditHours(e.target.value)} 
                        placeholder="e.g., 3"
                      />
                    </FormControl>
                    
                    <Checkbox 
                      isChecked={includeLab} 
                      onChange={(e) => setIncludeLab(e.target.checked)}
                    >
                      Subject includes lab component
                    </Checkbox>
                    
                    {includeLab && (
                      <HStack spacing={4}>
                        <FormControl>
                          <FormLabel>Theory Credits</FormLabel>
                          <Input 
                            type="number" 
                            value={theoryCredits} 
                            onChange={(e) => setTheoryCredits(e.target.value)} 
                          />
                        </FormControl>
                        <FormControl>
                          <FormLabel>Lab Credits</FormLabel>
                          <Input 
                            type="number" 
                            value={labCredits} 
                            onChange={(e) => setLabCredits(e.target.value)} 
                          />
                        </FormControl>
                      </HStack>
                    )}
                  </VStack>
                </TabPanel>
                
                {/* Components Tab */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Flex justify="space-between" wrap="wrap" gap={2}>
                      <Button leftIcon={<AddIcon />} onClick={handleAddComponent}>
                        Add Component
                      </Button>
                      <Button onClick={() => handleAddMultipleComponents("Quiz")}>
                        Add Multiple Quizzes
                      </Button>
                      <Button onClick={() => handleAddMultipleComponents("Assignment")}>
                        Add Multiple Assignments
                      </Button>
                    </Flex>
                    
                    {/* Total Weight Indicator */}
                    <Box>
                      <Flex justify="space-between" align="center">
                        <FormLabel mb="0">Total Weight:</FormLabel>
                        <Badge 
                          colorScheme={Math.abs(totalWeight - 100) < 0.01 ? "green" : "red"}
                          fontSize="md"
                          px={2}
                          py={1}
                          borderRadius="md"
                        >
                          {totalWeight.toFixed(1)}%
                        </Badge>
                      </Flex>
                      
                      {Math.abs(totalWeight - 100) > 0.01 && (
                        <Alert status="warning" mt={2} size="sm">
                          <AlertIcon />
                          Total weight should be 100%. Current total: {totalWeight.toFixed(1)}%.
                        </Alert>
                      )}
                    </Box>
                    
                    {components.length === 0 ? (
                      <p>No components added yet. Use the buttons above to add components.</p>
                    ) : (
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th>Component</Th>
                            <Th>Weight (%)</Th>
                            <Th>Max Marks</Th>
                            <Th>My Marks</Th>
                            <Th>Class Avg</Th>
                            <Th>Actions</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {components.map((comp, idx) => (
                            <Tr key={idx}>
                              <Td>{comp.name}</Td>
                              <Td>{comp.weight.toFixed(1)}</Td>
                              <Td>{comp.maxMarks}</Td>
                              <Td>{comp.myMarks}</Td>
                              <Td>{comp.classAvgMarks}</Td>
                              <Td>
                                <HStack spacing={1}>
                                  <IconButton
                                    icon={<EditIcon />}
                                    aria-label="Edit component"
                                    size="xs"
                                    onClick={() => handleEditComponent(comp, idx)}
                                  />
                                  <IconButton
                                    icon={<DeleteIcon />}
                                    aria-label="Delete component"
                                    size="xs"
                                    colorScheme="red"
                                    onClick={() => handleDeleteComponent(idx)}
                                  />
                                </HStack>
                              </Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    )}
                  </VStack>
                </TabPanel>
                
                {/* Presets Tab */}
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <FormControl>
                      <FormLabel>Select a preset</FormLabel>
                      <Select
                        value={selectedPreset}
                        onChange={(e) => setSelectedPreset(e.target.value)}
                      >
                        {Object.keys(SUBJECT_PRESETS).map(preset => (
                          <option key={preset} value={preset}>
                            {preset}
                          </option>
                        ))}
                      </Select>
                    </FormControl>
                    
                    <Button 
                      colorScheme="teal"
                      onClick={handleApplyPreset}
                      isDisabled={selectedPreset === 'Custom'}
                    >
                      Customize & Apply Preset
                    </Button>
                    
                    {selectedPreset !== 'Custom' && (
                      <VStack align="stretch" spacing={2}>
                        <h3>Preset Components:</h3>
                        <Table size="sm">
                          <Thead>
                            <Tr>
                              <Th>Component</Th>
                              <Th>Weight</Th>
                              <Th>Count</Th>
                              <Th>Group</Th>
                            </Tr>
                          </Thead>
                          <Tbody>
                            {SUBJECT_PRESETS[selectedPreset].map((item, idx) => (
                              <Tr key={idx}>
                                <Td>{item.name}</Td>
                                <Td>{item.weight}%</Td>
                                <Td>{item.count}</Td>
                                <Td>{item.isGroup ? "Yes" : "No"}</Td>
                              </Tr>
                            ))}
                          </Tbody>
                        </Table>
                      </VStack>
                    )}
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </ModalBody>
          
          <ModalFooter>
            <Button colorScheme="gray" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="teal" onClick={handleSave}>
              Save Subject
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      <ComponentDialog 
        isOpen={componentDialog.isOpen} 
        onClose={componentDialog.onClose}
        onSave={handleSaveComponent}
        component={currentComponent}
      />
      
      <MultiComponentDialog
        isOpen={multiComponentDialog.isOpen}
        onClose={multiComponentDialog.onClose}
        onSave={handleSaveMultipleComponents}
        params={multiComponentParams}
      />
      
      <PresetCustomizationDialog
        isOpen={presetCustomizationDialog.isOpen}
        onClose={presetCustomizationDialog.onClose}
        onApplyPreset={handleApplyCustomizedPreset}
        presetName={selectedPreset}
        presetComponents={presetToCustomize}
      />
      
      <SequentialDataEntryDialog
        isOpen={sequentialDataEntryDialog.isOpen}
        onClose={sequentialDataEntryDialog.onClose}
        onComplete={handleSequentialDataEntryComplete}
        customizedComponents={componentsToEnterData}
      />
    </React.Fragment>
  );
};

export default SubjectDialog;
