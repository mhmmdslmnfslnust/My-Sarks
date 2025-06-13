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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Text,
  Flex,
  Badge,
  Divider,
  Alert,
  AlertIcon,
  Box
} from '@chakra-ui/react';

const PresetCustomizationDialog = ({ isOpen, onClose, onApplyPreset, presetName, presetComponents }) => {
  const [components, setComponents] = useState([]);
  const [totalWeight, setTotalWeight] = useState(100);
  const [isValidWeight, setIsValidWeight] = useState(true);

  // Initialize with preset components when dialog opens
  useEffect(() => {
    if (isOpen && presetComponents) {
      setComponents([...presetComponents]);
      validateTotalWeight([...presetComponents]);
    }
  }, [isOpen, presetComponents]);

  // Validate that total weight equals 100%
  const validateTotalWeight = (comps) => {
    const total = comps.reduce((sum, comp) => sum + comp.weight, 0);
    setTotalWeight(total);
    setIsValidWeight(Math.abs(total - 100) < 0.01); // Allow for tiny rounding errors
    return Math.abs(total - 100) < 0.01;
  };

  // Handle changes to component count
  const handleCountChange = (index, value) => {
    const newComponents = [...components];
    newComponents[index].count = value;
    setComponents(newComponents);
  };

  // Handle changes to component weight
  const handleWeightChange = (index, value) => {
    const newComponents = [...components];
    newComponents[index].weight = value;
    setComponents(newComponents);
    validateTotalWeight(newComponents);
  };

  // Apply the customized preset
  const handleApply = () => {
    // Final validation
    if (validateTotalWeight(components)) {
      // Format components more appropriately for sequential entry
      const formattedComponents = components.map(comp => {
        // For group components like quizzes, create individual named items
        if (comp.isGroup && comp.count > 1) {
          const items = [];
          const weightPerItem = comp.weight / comp.count;
          
          for (let i = 1; i <= comp.count; i++) {
            items.push({
              name: `${comp.name} ${i}`,
              weight: weightPerItem,
              isGroup: false,
              count: 1
            });
          }
          return items;
        } else {
          // Single component
          return [{
            name: comp.name,
            weight: comp.weight,
            isGroup: false,
            count: 1
          }];
        }
      }).flat();
      
      onApplyPreset(formattedComponents);
      onClose();
    } else {
      alert("Total weight must equal 100%. Please adjust component weights.");
    }
  };

  // Normalize weights to sum to 100%
  const normalizeWeights = () => {
    if (totalWeight === 0) return;

    const newComponents = components.map(comp => ({
      ...comp,
      weight: (comp.weight / totalWeight) * 100
    }));
    
    setComponents(newComponents);
    validateTotalWeight(newComponents);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Customize {presetName} Preset</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Text mb={4}>
            Customize the component parameters before applying this preset.
            Ensure the total weight equals 100%.
          </Text>

          {!isValidWeight && (
            <Alert status="warning" mb={4}>
              <AlertIcon />
              Total weight: {totalWeight.toFixed(1)}%. Should be 100%.
              <Button size="sm" ml={4} onClick={normalizeWeights}>Normalize</Button>
            </Alert>
          )}

          <Divider my={4} />

          <Table variant="simple" size="sm">
            <Thead>
              <Tr>
                <Th>Component</Th>
                <Th>Count</Th>
                <Th>Weight (%)</Th>
                <Th>Group</Th>
              </Tr>
            </Thead>
            <Tbody>
              {components.map((comp, idx) => (
                <Tr key={idx}>
                  <Td>{comp.name}</Td>
                  <Td>
                    <NumberInput
                      min={1}
                      max={20}
                      value={comp.count}
                      onChange={(_, value) => handleCountChange(idx, value)}
                      size="sm"
                      w="80px"
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
                      min={1}
                      max={100}
                      value={comp.weight}
                      onChange={(_, value) => handleWeightChange(idx, value)}
                      size="sm"
                      w="80px"
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </Td>
                  <Td>
                    {comp.isGroup ? (
                      <Badge colorScheme="green">Yes</Badge>
                    ) : (
                      <Badge colorScheme="gray">No</Badge>
                    )}
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          <Box mt={4}>
            <Flex justify="space-between">
              <Text>Total Weight:</Text>
              <Text 
                fontWeight="bold" 
                color={isValidWeight ? "green.500" : "red.500"}
              >
                {totalWeight.toFixed(1)}%
              </Text>
            </Flex>
          </Box>

          <Divider my={4} />

          <Text fontSize="sm" color="gray.600">
            Note: Group components (like quizzes) will be created as individual items with equal distribution of their total weight.
          </Text>
        </ModalBody>
        
        <ModalFooter>
          <Button colorScheme="gray" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button 
            colorScheme="teal" 
            onClick={handleApply}
            isDisabled={!isValidWeight}
          >
            Apply Customized Preset
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default PresetCustomizationDialog;
