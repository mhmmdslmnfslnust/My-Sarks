import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Checkbox,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Text,
  VStack,
  HStack,
  Badge,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  IconButton,
  useDisclosure
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { Semester } from '../models';
import SubjectDialog from './dialogs/SubjectDialog';

const SubjectEntryScreen = ({ gradeScale, onComplete }) => {
  const [subjects, setSubjects] = useState([]);
  const [includePrevious, setIncludePrevious] = useState(false);
  const [previousCgpa, setPreviousCgpa] = useState('');
  const [previousCredits, setPreviousCredits] = useState('');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [currentSubject, setCurrentSubject] = useState(null);
  const [editIndex, setEditIndex] = useState(null);

  const handleAddSubject = () => {
    setCurrentSubject(null);
    setEditIndex(null);
    onOpen();
  };

  const handleEditSubject = (subject, index) => {
    setCurrentSubject(subject);
    setEditIndex(index);
    onOpen();
  };

  const handleDeleteSubject = (index) => {
    if (window.confirm(`Are you sure you want to delete ${subjects[index].name}?`)) {
      const newSubjects = [...subjects];
      newSubjects.splice(index, 1);
      setSubjects(newSubjects);
    }
  };

  const handleSaveSubject = (subject) => {
    if (editIndex !== null) {
      const newSubjects = [...subjects];
      newSubjects[editIndex] = subject;
      setSubjects(newSubjects);
    } else {
      setSubjects([...subjects, subject]);
    }
    onClose();
  };

  const handleCalculateResults = () => {
    if (subjects.length === 0) {
      alert("Please add at least one subject before calculating results.");
      return;
    }

    let prevCgpa = null;
    let prevCredits = null;

    if (includePrevious) {
      try {
        if (previousCgpa) {
          prevCgpa = parseFloat(previousCgpa);
        }
        if (previousCredits) {
          prevCredits = parseFloat(previousCredits);
        }
      } catch (e) {
        alert("Please enter valid numbers for CGPA and credits.");
        return;
      }
    }

    const semester = new Semester("Current Semester", subjects, prevCgpa, prevCredits);
    onComplete(semester);
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading as="h1" size="xl" textAlign="center">
          Subject Entry
        </Heading>

        {/* Previous CGPA Section */}
        <Card>
          <CardHeader>
            <Heading size="md">Previous CGPA (Optional)</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <Checkbox
                isChecked={includePrevious}
                onChange={(e) => setIncludePrevious(e.target.checked)}
              >
                Include previous CGPA data
              </Checkbox>
              
              {includePrevious && (
                <>
                  <Flex gap={4} direction={["column", "row"]}>
                    <FormControl>
                      <FormLabel>Previous CGPA:</FormLabel>
                      <Input 
                        type="number" 
                        value={previousCgpa} 
                        onChange={(e) => setPreviousCgpa(e.target.value)}
                      />
                    </FormControl>
                    <FormControl>
                      <FormLabel>Previous Credits:</FormLabel>
                      <Input 
                        type="number" 
                        value={previousCredits} 
                        onChange={(e) => setPreviousCredits(e.target.value)}
                      />
                    </FormControl>
                  </Flex>
                </>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Subjects Section */}
        <Card>
          <CardHeader>
            <Flex justify="space-between" align="center">
              <Heading size="md">Subjects</Heading>
              <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={handleAddSubject}>
                Add Subject
              </Button>
            </Flex>
          </CardHeader>
          <CardBody>
            {subjects.length === 0 ? (
              <Text textAlign="center" color="gray.500">
                No subjects added yet. Click 'Add Subject' to begin.
              </Text>
            ) : (
              <VStack spacing={4} align="stretch">
                {subjects.map((subject, idx) => (
                  <Card key={idx} variant="outline">
                    <CardHeader pb={0}>
                      <Flex justify="space-between" align="center">
                        <Heading size="md">{subject.name}</Heading>
                        <Badge colorScheme="blue">{subject.creditHours} credits</Badge>
                      </Flex>
                    </CardHeader>
                    <CardBody>
                      <Table size="sm" variant="simple">
                        <Thead>
                          <Tr>
                            <Th>Component</Th>
                            <Th>Weight</Th>
                            <Th>My Score</Th>
                            <Th>Class Avg</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {subject.components.map((comp, compIdx) => (
                            <Tr key={compIdx}>
                              <Td>{comp.name}</Td>
                              <Td>{comp.weight.toFixed(1)}%</Td>
                              <Td>{comp.myMarks}/{comp.maxMarks}</Td>
                              <Td>{comp.classAvgMarks}/{comp.maxMarks}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </CardBody>
                    <CardFooter pt={0}>
                      <Flex gap={2}>
                        <IconButton
                          icon={<EditIcon />}
                          aria-label="Edit subject"
                          size="sm"
                          onClick={() => handleEditSubject(subject, idx)}
                        />
                        <IconButton
                          icon={<DeleteIcon />}
                          aria-label="Delete subject"
                          size="sm"
                          colorScheme="red"
                          onClick={() => handleDeleteSubject(idx)}
                        />
                      </Flex>
                    </CardFooter>
                  </Card>
                ))}
              </VStack>
            )}
          </CardBody>
        </Card>

        <Flex justify="flex-end" mt={4}>
          <Button 
            colorScheme="teal" 
            size="lg"
            onClick={handleCalculateResults}
          >
            Calculate Results
          </Button>
        </Flex>
      </VStack>

      <SubjectDialog
        isOpen={isOpen}
        onClose={onClose}
        onSave={handleSaveSubject}
        subject={currentSubject}
      />
    </Container>
  );
};

export default SubjectEntryScreen;
