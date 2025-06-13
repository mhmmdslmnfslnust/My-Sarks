# Academic Performance Tracker (Web Version)

A web-based application for tracking academic performance across courses and semesters. This is the web version of the My-Sarks desktop application.

## Features

- Customizable grade scale based on relative performance
- Add and manage multiple subjects with their components
- Calculate expected grades based on your performance relative to class averages
- Track semester and cumulative GPA
- Visualize performance with charts and detailed breakdowns
- Save results for future reference

## Getting Started

### Prerequisites

- Node.js (v14 or newer)
- npm or yarn

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/My-Sarks.git
   cd My-Sarks/web
   ```

2. Install dependencies:
   ```
   npm install
   # or
   yarn install
   ```

3. Start the development server:
   ```
   npm start
   # or
   yarn start
   ```

4. Open http://localhost:3000 to view the app in your browser.

### Building for Production

To create an optimized production build:
```
npm run build
# or
yarn build
```

The build artifacts will be stored in the `build/` directory.

## How It Works

1. **Grade Scale Configuration**:
   - Start by configuring your grade scale or use the default
   - The grade scale determines how your relative performance translates to letter grades

2. **Subject Entry**:
   - Add all your subjects and their components (exams, assignments, quizzes, etc.)
   - Enter your marks, maximum possible marks, and class average for each component

3. **Results**:
   - View calculated grades, GPA, and detailed performance analysis
   - See visual representations of your standing in each course
   - Save the results as a JSON file for record keeping

## Technologies Used

- React
- Chakra UI
- Chart.js
- React Router

## License

This project is licensed under the MIT License - see the LICENSE file for details.
