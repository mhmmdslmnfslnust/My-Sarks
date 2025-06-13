import React, { useState } from 'react';
import { ChakraProvider, Box, VStack, Heading, Text, extendTheme } from '@chakra-ui/react';
import GradeScaleScreen from './components/GradeScaleScreen';
import SubjectEntryScreen from './components/SubjectEntryScreen';
import ResultsScreen from './components/ResultsScreen';
import { generateSemesterSummary } from './utils/calculator';

// Define a custom theme
const theme = extendTheme({
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      }
    }
  },
  colors: {
    brand: {
      50: '#e6f6ff',
      100: '#bae3ff',
      200: '#7cc4fa',
      300: '#47a3f3',
      400: '#2186eb',
      500: '#0967d2',
      600: '#0552b5',
      700: '#03449e',
      800: '#01337d',
      900: '#002159',
    }
  }
});

function App() {
  const [currentScreen, setCurrentScreen] = useState('gradeScale');
  const [gradeScale, setGradeScale] = useState(null);
  const [semester, setSemester] = useState(null);
  const [semesterSummary, setSemesterSummary] = useState(null);

  const handleGradeScaleComplete = (scale) => {
    setGradeScale(scale);
    setCurrentScreen('subjectEntry');
  };

  const handleSubjectEntryComplete = (semesterData) => {
    setSemester(semesterData);
    const summary = generateSemesterSummary(semesterData, gradeScale);
    setSemesterSummary(summary);
    setCurrentScreen('results');
  };

  const handleReset = () => {
    setCurrentScreen('gradeScale');
    setSemester(null);
    setSemesterSummary(null);
  };

  return (
    <ChakraProvider theme={theme}>
      <VStack minH="100vh" bg="gray.50" pt={8} pb={16}>
        <Box textAlign="center" mb={8}>
          <Heading as="h1" size="2xl" color="brand.700">Academic Performance Tracker</Heading>
          <Text fontSize="lg" color="gray.600" mt={2}>
            Calculate and track your semester performance
          </Text>
        </Box>
        
        <Box w="full" maxW="1200px" mx="auto" px={4}>
          {currentScreen === 'gradeScale' && (
            <GradeScaleScreen onComplete={handleGradeScaleComplete} />
          )}
          
          {currentScreen === 'subjectEntry' && (
            <SubjectEntryScreen 
              gradeScale={gradeScale} 
              onComplete={handleSubjectEntryComplete} 
            />
          )}
          
          {currentScreen === 'results' && (
            <ResultsScreen 
              semesterSummary={semesterSummary} 
              onReset={handleReset}
            />
          )}
        </Box>
        
        <Text fontSize="sm" color="gray.500" position="absolute" bottom={4}>
          &copy; {new Date().getFullYear()} Academic Performance Tracker | My-Sarks
        </Text>
      </VStack>
    </ChakraProvider>
  );
}

export default App;
