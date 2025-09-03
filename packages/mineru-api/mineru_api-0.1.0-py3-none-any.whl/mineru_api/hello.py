"""
Simple hello world module for a2astore package
"""


def hello_world(name: str = "World") -> str:
    """
    Return a hello world greeting.
    
    Args:
        name (str): Name to greet. Defaults to "World".
        
    Returns:
        str: Greeting message
    """
    return f"Hello, {name}! Welcome to A2A Store!"


def main():
    """Main function for command line usage"""
    print(hello_world())


if __name__ == "__main__":
    main()
