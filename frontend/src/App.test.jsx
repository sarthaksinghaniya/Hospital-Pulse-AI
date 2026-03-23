import { render, screen } from '@testing-library/react'
import App from '../App'

test('renders Hospital Pulse AI title', () => {
  render(<App />)
  const titleElement = screen.getByText(/Hospital Pulse AI/i)
  expect(titleElement).toBeInTheDocument()
})