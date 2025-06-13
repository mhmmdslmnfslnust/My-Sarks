import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Text,
  VStack,
  SimpleGrid
} from '@chakra-ui/react';
import { createDefaultGradeScale } from '../utils/calculator';
import { GradeScale } from '../models';

const GradeScaleScreen = ({ onComplete }) => {
  const defaultGradeScale = createDefaultGradeScale();
  const [thresholds, setThresholds] = useState(() => {
    // Convert the grade scale thresholds to percentage values for display
    const initialThresholds = {};
    Object.entries(defaultGradeScale.thresholds).forEach(([threshold, [grade, points]]) => {
      initialThresholds[grade] = parseFloat(threshold) * 100;
    });
    return initialThresholds;
  });

  const handleThresholdChange = (grade, value) => {
    setThresholds(prev => ({
      ...prev,
      [grade]: value
    }));
  };

  const handleUseDefault = () => {
    onComplete(createDefaultGradeScale());
  };

  const handleSaveAndContinue = () => {
    try {
      const newThresholds = {};
      const grades = Object.keys(thresholds);
      
      // Find grade points for each grade
      grades.forEach(grade => {
        const threshold = parseFloat(thresholds[grade]) / 100; // Convert percentage to decimal
        const gradePoints = getGradePoints(grade);
        newThresholds[threshold] = [grade, gradePoints];
      });
      
      const customGradeScale = new GradeScale(newThresholds);
      onComplete(customGradeScale);
    } catch (error) {
      console.error("Error creating grade scale:", error);
      alert("Please enter valid numbers for all thresholds.");
    }
  };

  const getGradePoints = (grade) => {
    // Find the corresponding grade points for this grade
    for (const [, [g, points]] of Object.entries(defaultGradeScale.thresholds)) {
      if (g === grade) {
        return points;
      }
    }
    return 0;
  };

  // Create sorted array of grades and their points
  const grades = [
    { letter: 'A', points: 4.0 },
    { letter: 'B+', points: 3.5 },
    { letter: 'B', points: 3.0 },
    { letter: 'C+', points: 2.5 },
    { letter: 'C', points: 2.0 },
    { letter: 'D+', points: 1.5 },
    { letter: 'D', points: 1.0 },
    { letter: 'F', points: 0.0 }
  ];

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading as="h1" size="xl" textAlign="center">
          Customize Grade Scale
        </Heading>
        <Text textAlign="center">
          Enter relative performance thresholds (as percentages)
        </Text>
        
        <SimpleGrid columns={[1, null, 2]} spacing={4} mt={4}>
          {grades.map(({ letter, points }) => (
            <FormControl key={letter}>
              <FormLabel>
                {letter} ({points} points) threshold:
              </FormLabel>
              <Flex>
                <Input 
                  type="number" 
                  value={thresholds[letter] || 0}
                  onChange={(e) => handleThresholdChange(letter, e.target.value)} 
                  mr={2}
                />
                <Text alignSelf="center">%</Text>
              </Flex>
            </FormControl>
          ))}
        </SimpleGrid>
        
        <Flex direction={["column", "row"]} justify="space-between" gap={4} mt={4}>
          <Button 
            colorScheme="gray" 
            onClick={handleUseDefault}
          >
            Use Default Scale
          </Button>
          <Button 
            colorScheme="teal" 
            onClick={handleSaveAndContinue}
          >
            Continue
          </Button>
        </Flex>
      </VStack>
    </Container>
  );
};

export default GradeScaleScreen;
