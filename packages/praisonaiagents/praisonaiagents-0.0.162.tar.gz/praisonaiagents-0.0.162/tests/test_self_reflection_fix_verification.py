#!/usr/bin/env python3
"""Test to verify the self-reflection fix works with tools"""

from praisonaiagents import Agent, Task, PraisonAIAgents
from praisonaiagents.tools import calculator

def test_self_reflection_fix_verification():
    """Test that self-reflection now works with tools"""
    print("=== Testing Self-Reflection Fix Verification ===")
    
    # Create an agent with self-reflection enabled and tools
    agent = Agent(
        name="MathAgent",
        role="Math Assistant",
        goal="Solve mathematical problems accurately",
        backstory="You are a helpful math assistant who double-checks calculations",
        tools=[calculator],
        self_reflect=True,  # This should now work with tools
        min_reflect=1,
        max_reflect=2,
        verbose=True
    )

    # Define a task that would benefit from self-reflection
    task = Task(
        description="Calculate 123 * 456 and verify the result is correct",
        expected_output="The calculation result with verification",
        agent=agent,
        name="math_calculation"
    )

    # Create and run the agents
    agents = PraisonAIAgents(
        agents=[agent],
        tasks=[task],
        process="sequential"
    )
    
    try:
        result = agents.start()
        
        assert result, "Self-reflection with tools failed to produce a result."
        print("\n✅ SUCCESS: Self-reflection with tools is working!")
        print(f"Result: {result}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise AssertionError(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_self_reflection_fix_verification()