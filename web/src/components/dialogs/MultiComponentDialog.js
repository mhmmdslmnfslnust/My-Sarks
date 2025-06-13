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
  Radio,
  RadioGroup,
  VStack,
  HStack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td
} from '@chakra-ui/react';
import { Component } from '../../models';

const MultiComponentDialog = ({ isOpen, onClose, onSave, params }) => {
  const [baseName, setBaseName] = useState('');
  const [count, setCount] = useState(4);
  const [totalWeight, setTotalWeight] = useState(10);
  const [distributionMethod, setDistributionMethod] = useState('equal');
  const [componentData, setComponentData] = useState([]);

  // Initialize form when dialog opens
  useEffect(() => {
    if (isOpen && params) {
      setBaseName(params.baseName);
      setCount(params.count);
      setTotalWeight(params.totalWeight);
      generateEmptyComponentData(params.count);
    }
  }, [isOpen, params]);

  const generateEmptyComponentData = (count) => {
    const data = [];
    for (let i = 0; i < count; i++) {
      data.push({
        maxMarks: 10,
        myMarks: 0,
        classAvgMarks: 0
      });
    }
    setComponentData(data);
  };

  const handleCountChange = (e) => {
    const newCount = parseInt(e.target.value);
    if (newCount > 0) {
      setCount(newCount);
      generateEmptyComponentData(newCount);
    }
  };

  const handleComponentDataChange = (index, field, value) => {
    const newData = [...componentData];
    newData[index] = {
      ...newData[index],
      [field]: parseFloat(value)
    };
    setComponentData(newData);
  };

  const handleSave = () => {
    try {
      if (count <= 0) {
        alert("Count must be at least 1.");
        return;
      }
      
      if (totalWeight <= 0) {
        alert("Total weight must be greater than zero.");
        return;
      }
      
      // Validate all component data
      for (let i = 0; i < count; i++) {
        const data = componentData[i];
        if (!data) continue;
        
        if (data.maxMarks <= 0) {
          alert(`Max marks for ${baseName} ${i+1} must be greater than zero.`);
          return;
        }
        
        if (data.myMarks < 0 || data.myMarks > data.maxMarks) {
          alert(`My marks for ${baseName} ${i+1} must be between 0 and ${data.maxMarks}.`);
          return;
        }
        
        if (data.classAvgMarks < 0 || data.classAvgMarks > data.maxMarks) {
          alert(`Class average for ${baseName} ${i+1} must be between 0 and ${data.maxMarks}.`);
          return;
        }
      }
      
      // Calculate individual weights
      let individualWeights = [];
      
      if (distributionMethod === 'equal') {
        // Equal weight distribution
        const weightPerItem = totalWeight / count;
        individualWeights = Array(count).fill(weightPerItem);
      } else {
        // Weighted by max marks
        const totalMaxMarks = componentData.reduce((sum, data) => sum + data.maxMarks, 0);
        if (totalMaxMarks > 0) {
          individualWeights = componentData.map(data => 
            (data.maxMarks / totalMaxMarks) * totalWeight
          );
        } else {
          // Fallback to equal distribution
          const weightPerItem = totalWeight / count;
          individualWeights = Array(count).fill(weightPerItem);
        }
      }
      
      // Create components
      const components = [];
      for (let i = 0; i < count; i++) {
        const data = componentData[i];
        components.push(new Component(
          `${baseName} ${i+1}`,
          individualWeights[i],
          data.maxMarks,
          data.myMarks,
          data.classAvgMarks
        ));
      }
      
      onSave(components);
    } catch (error) {
      alert("Please enter valid numbers for all fields.");
      console.error(error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add Multiple {baseName}s</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={6} align="stretch">
            <FormControl>
              <FormLabel>Number of {baseName}s</FormLabel>
              <Input 
                type="number" 
                value={count} 
                onChange={handleCountChange} 
                width="100px"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Total weight for all {baseName}s (%)</FormLabel>
              <Input 
                type="number" 
                value={totalWeight} 
                onChange={(e) => setTotalWeight(parseFloat(e.target.value))} 
                width="100px"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Weight distribution method</FormLabel>
              <RadioGroup value={distributionMethod} onChange={setDistributionMethod}>
                <HStack spacing={4}>
                  <Radio value="equal">Equal weight for each</Radio>
                  <Radio value="by_marks">Weighted by max marks</Radio>
                </HStack>
              </RadioGroup>
            </FormControl>
            
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>{baseName} #</Th>
                  <Th>Max Marks</Th>
                  <Th>My Marks</Th>
                  <Th>Class Average</Th>
                </Tr>
              </Thead>
              <Tbody>
                {Array.from({ length: count }).map((_, idx) => (
                  <Tr key={idx}>
                    <Td>{baseName} {idx+1}</Td>
                    <Td>
                      <Input 
                        type="number" 
                        size="sm"
                        value={componentData[idx]?.maxMarks || 10} 
                        onChange={(e) => handleComponentDataChange(idx, 'maxMarks', e.target.value)}
                      />
                    </Td>
                    <Td>
                      <Input 
                        type="number" 
                        size="sm"
                        value={componentData[idx]?.myMarks || 0} 
                        onChange={(e) => handleComponentDataChange(idx, 'myMarks', e.target.value)}
                      />
                    </Td>
                    <Td>
                      <Input 
                        type="number" 
                        size="sm"
                        value={componentData[idx]?.classAvgMarks || 0} 
                        onChange={(e) => handleComponentDataChange(idx, 'classAvgMarks', e.target.value)}
                      />
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
          <Button colorScheme="teal" onClick={handleSave}>
            Save All Components
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default MultiComponentDialog;
