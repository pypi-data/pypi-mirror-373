# React TypeScript Analyzer Command

```yaml
description: Analyze React TypeScript application architecture, performance, and patterns
argument-hint:
  [analysis request, e.g., 'find all custom hooks', 'identify bundle size issues', 'check component patterns']
```

First, execute `/mcp__serena__initial_instructions` to initialize Serena MCP for enhanced semantic analysis.

Then, call the **react-ts-analyzer** sub agent to perform comprehensive React TypeScript application analysis.

Analyze the following React TypeScript request:

- **Component Architecture Analysis**
  - Component hierarchy and composition patterns
  - Props drilling and state management analysis
  - Component size and complexity metrics
  - Reusability and coupling assessment

- **TypeScript Integration Analysis**
  - Type safety coverage and any usage
  - Interface and type definition organization
  - Generic usage patterns and optimization
  - Type assertion and casting patterns

- **Performance Analysis**
  - Bundle size analysis and code splitting opportunities
  - Re-render patterns and optimization opportunities
  - Memory leaks in useEffect and event listeners
  - Lazy loading and dynamic import usage

- **React Patterns and Best Practices**
  - Custom hooks identification and analysis
  - Context usage patterns and provider optimization
  - State management patterns (useState, useReducer, external libs)
  - Side effect management and cleanup

- **Build and Dependency Analysis**
  - Package.json dependency audit
  - Webpack/Vite configuration analysis
  - Tree shaking effectiveness
  - Dead code elimination opportunities

- **Code Quality and Maintainability**
  - Component testability assessment
  - Error boundary implementation
  - Accessibility compliance checking
  - Code duplication and refactoring opportunities

- **Security Analysis**
  - XSS vulnerability patterns
  - Unsafe dangerouslySetInnerHTML usage
  - Third-party dependency security audit
  - Environment variable exposure risks

$ARGUMENTS

## Usage Examples

```bash
# Analyze component architecture
react-ts-analyzer "analyze component hierarchy and identify tightly coupled components"

# Performance analysis
react-ts-analyzer "find performance bottlenecks and suggest optimization strategies"

# TypeScript usage analysis
react-ts-analyzer "check type safety coverage and identify areas using any type"

# Custom hook analysis
react-ts-analyzer "find all custom hooks and analyze their reusability patterns"

# Bundle analysis
react-ts-analyzer "analyze bundle size and identify code splitting opportunities"

# State management analysis
react-ts-analyzer "analyze state management patterns and identify prop drilling issues"
```

## Additional Specialized Queries

- **Testing Analysis**: Identify untested components and suggest testing strategies
- **Routing Analysis**: Analyze React Router setup and route organization
- **API Integration**: Analyze data fetching patterns and error handling
- **Styling Analysis**: CSS-in-JS usage, styled-components patterns, or CSS modules analysis
- **Accessibility Audit**: WCAG compliance and semantic HTML usage
- **SEO Analysis**: Meta tags, structured data, and SSR/SSG implementation