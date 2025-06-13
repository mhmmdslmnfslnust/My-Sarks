import React, { useRef } from 'react';
import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Text,
  VStack,
  HStack,
  Card,
  CardHeader,
  CardBody,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Divider,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  SimpleGrid
} from '@chakra-ui/react';
import { DownloadIcon } from '@chakra-ui/icons';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ResultsScreen = ({ semesterSummary, onReset }) => {
  const toast = useToast();
  const chartRef = useRef();

  // Function to save results as JSON
  const saveResults = () => {
    const dataStr = "data:text/json;charset=utf-8," + 
      encodeURIComponent(JSON.stringify(semesterSummary, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "academic_results.json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
    
    toast({
      title: "Results saved",
      description: "Your results have been saved to a JSON file.",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
  };

  // Get grade colors for visual representation
  const getGradeColor = (grade) => {
    const gradeColors = {
      'A': '#48BB78', // green
      'B+': '#68D391', // light green
      'B': '#4299E1', // blue
      'C+': '#63B3ED', // light blue
      'C': '#ECC94B', // yellow
      'D+': '#F6AD55', // orange
      'D': '#F56565', // red
      'F': '#9B2C2C', // dark red
    };
    return gradeColors[grade] || '#A0AEC0'; // gray default
  };

  // Get color based on relative performance
  const getRelativePerformanceColor = (value) => {
    if (value > 20) return 'green.500';
    if (value > 10) return 'green.400';
    if (value > 5) return 'green.300';
    if (value > 0) return 'green.200';
    if (value > -5) return 'yellow.200';
    if (value > -10) return 'orange.200';
    if (value > -20) return 'orange.400';
    return 'red.400';
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Flex justify="space-between" align="center">
          <Heading as="h1" size="xl">Academic Performance Results</Heading>
          <HStack>
            <Button leftIcon={<DownloadIcon />} onClick={saveResults}>
              Save Results
            </Button>
            <Button colorScheme="gray" onClick={onReset}>
              Start New Analysis
            </Button>
          </HStack>
        </Flex>

        {/* Overall stats card */}
        <Card>
          <CardHeader>
            <Heading size="md">Semester Summary</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
              <Stat>
                <StatLabel>Semester GPA (SGPA)</StatLabel>
                <StatNumber>{semesterSummary.sgpa.toFixed(2)}</StatNumber>
                <StatHelpText>{semesterSummary.totalCredits} credits this semester</StatHelpText>
              </Stat>
              
              {semesterSummary.cgpa !== null && (
                <Stat>
                  <StatLabel>Cumulative GPA (CGPA)</StatLabel>
                  <StatNumber>{semesterSummary.cgpa.toFixed(2)}</StatNumber>
                  <StatHelpText>Including {semesterSummary.previousCredits} previous credits</StatHelpText>
                </Stat>
              )}
              
              <Stat>
                <StatLabel>Subjects</StatLabel>
                <StatNumber>{semesterSummary.subjects.length}</StatNumber>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Grade Distribution Chart */}
        {semesterSummary.subjects.length > 0 && (
          <Card>
            <CardHeader>
              <Heading size="md">Grade Distribution</Heading>
            </CardHeader>
            <CardBody>
              <Box height="300px">
                <Bar 
                  ref={chartRef}
                  data={{
                    labels: semesterSummary.subjects.map(s => s.name.split(' ').slice(0, 2).join(' ')), // First two words of subject name
                    datasets: [
                      {
                        label: 'Grade Points',
                        data: semesterSummary.subjects.map(s => s.gradePoints),
                        backgroundColor: semesterSummary.subjects.map(s => getGradeColor(s.predictedGrade)),
                      },
                    ],
                  }}
                  options={{
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 4.0,
                        title: {
                          display: true,
                          text: 'Grade Points'
                        }
                      },
                      x: {
                        title: {
                          display: true,
                          text: 'Subjects'
                        }
                      }
                    },
                    plugins: {
                      tooltip: {
                        callbacks: {
                          afterLabel: function(context) {
                            const subject = semesterSummary.subjects[context.dataIndex];
                            return [
                              `Grade: ${subject.predictedGrade}`,
                              `Credits: ${subject.creditHours}`,
                              `Relative: ${subject.relativePerformancePercentage.toFixed(1)}%`
                            ];
                          }
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardBody>
          </Card>
        )}

        {/* Subjects accordion */}
        <Heading size="md" mt={4}>Subject Details</Heading>
        <Accordion allowMultiple defaultIndex={[0]}>
          {semesterSummary.subjects.map((subject, idx) => (
            <AccordionItem key={idx}>
              <h2>
                <AccordionButton>
                  <Box flex="1" textAlign="left">
                    <HStack>
                      <Text fontWeight="bold">{subject.name}</Text>
                      <Badge colorScheme="blue">{subject.creditHours} credits</Badge>
                      <Badge bg={getGradeColor(subject.predictedGrade)} color="white">
                        {subject.predictedGrade} ({subject.gradePoints.toFixed(1)})
                      </Badge>
                    </HStack>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                {/* Subject summary stats */}
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={4}>
                  <Card variant="outline" p={3}>
                    <Stat>
                      <StatLabel>My Score</StatLabel>
                      <StatNumber>{subject.weightedMyScore.toFixed(1)}%</StatNumber>
                      <StatHelpText>Raw: {subject.myTotalRaw}/{subject.maxTotalRaw}</StatHelpText>
                    </Stat>
                  </Card>
                  
                  <Card variant="outline" p={3}>
                    <Stat>
                      <StatLabel>Class Average</StatLabel>
                      <StatNumber>{subject.weightedClassAvg.toFixed(1)}%</StatNumber>
                      <StatHelpText>Raw: {subject.classAvgRaw}/{subject.maxTotalRaw}</StatHelpText>
                    </Stat>
                  </Card>
                  
                  <Card variant="outline" p={3}>
                    <Stat>
                      <StatLabel>Relative Performance</StatLabel>
                      <StatNumber color={getRelativePerformanceColor(subject.relativePerformancePercentage)}>
                        {subject.relativePerformancePercentage.toFixed(1)}%
                      </StatNumber>
                      <Progress 
                        value={50 + subject.relativePerformancePercentage/2}
                        colorScheme={subject.relativePerformancePercentage >= 0 ? "green" : "red"}
                        size="sm"
                        mt={2}
                      />
                    </Stat>
                  </Card>
                </SimpleGrid>
                
                <Divider my={4} />
                
                {/* Components table */}
                <Heading size="sm" mb={3}>Component Breakdown</Heading>
                <Table size="sm" variant="simple" mb={4}>
                  <Thead>
                    <Tr>
                      <Th>Component</Th>
                      <Th isNumeric>Weight</Th>
                      <Th isNumeric>My Score</Th>
                      <Th isNumeric>Class Avg</Th>
                      <Th isNumeric>Relative</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {subject.components.map((comp, compIdx) => (
                      <Tr key={compIdx}>
                        <Td>{comp.name}</Td>
                        <Td isNumeric>{comp.weight.toFixed(1)}%</Td>
                        <Td isNumeric>
                          {comp.myMarks}/{comp.maxMarks} ({comp.myPercentage.toFixed(1)}%)
                        </Td>
                        <Td isNumeric>
                          {comp.classAvgMarks}/{comp.maxMarks} ({comp.classAvgPercentage.toFixed(1)}%)
                        </Td>
                        <Td 
                          isNumeric 
                          color={getRelativePerformanceColor(comp.relativePerformancePercentage)}
                          fontWeight="bold"
                        >
                          {comp.relativePerformancePercentage.toFixed(1)}%
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </AccordionPanel>
            </AccordionItem>
          ))}
        </Accordion>
      </VStack>
    </Container>
  );
};

export default ResultsScreen;
