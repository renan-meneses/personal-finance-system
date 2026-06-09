import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../src/context/ThemeContext";
import { AuthProvider } from "../src/context/AuthContext";
import ThemeToggle from "../src/components/ThemeToggle";
import { type ReactNode } from "react";

// Mock the api module
vi.mock("../src/services/api", () => ({
  getProfile: vi.fn().mockResolvedValue({
    id: 1,
    username: "testuser",
    email: "test@test.com",
    theme_preference: "light",
    monthly_income: "5000",
  }),
  updateTheme: vi.fn().mockResolvedValue({ theme_preference: "dark" }),
  login: vi.fn(),
  logout: vi.fn(),
}));

function TestWrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <ThemeProvider>{children}</ThemeProvider>
    </AuthProvider>
  );
}

describe("ThemeToggle", () => {
  beforeEach(() => {
    document.documentElement.classList.remove("dark");
  });

  it("renders the toggle button", async () => {
    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );

    const button = await screen.findByRole("button", { name: /switch to/i });
    expect(button).toBeInTheDocument();
  });

  it("toggles theme from light to dark on click", async () => {
    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );

    // Wait for auth to resolve and theme to load
    const button = await screen.findByRole("button", { name: /switch to dark mode/i });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);

    // After click, should show "Switch to light mode"
    const switchedButton = await screen.findByRole("button", {
      name: /switch to light mode/i,
    });
    expect(switchedButton).toBeInTheDocument();
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("calls the API when toggling", async () => {
    const api = await import("../src/services/api");

    render(
      <TestWrapper>
        <ThemeToggle />
      </TestWrapper>
    );

    const button = await screen.findByRole("button", { name: /switch to dark mode/i });
    fireEvent.click(button);

    expect(api.updateTheme).toHaveBeenCalledWith("dark");
  });
});
