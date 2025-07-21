import { exec } from 'child_process';

// Start both React and Flask servers concurrently
console.log('🚀 Starting React + Flask development servers...');
console.log('📦 React frontend: http://localhost:5000');
console.log('🔗 Flask backend: http://localhost:8000');

const bothProcess = exec('npx concurrently "npx vite --host 0.0.0.0 --port 5000" "cd server && python simple_flask.py" --names "React,Flask" --prefix-colors "cyan,yellow"', (error, stdout, stderr) => {
  if (error) {
    console.error('Server error:', error);
  }
  if (stdout) {
    console.log(stdout);
  }
  if (stderr) {
    console.error(stderr);
  }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('🛑 Shutting down servers...');
  bothProcess.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down servers...');
  bothProcess.kill();
  process.exit(0);
});

console.log('✅ React + Flask servers starting with concurrently...');