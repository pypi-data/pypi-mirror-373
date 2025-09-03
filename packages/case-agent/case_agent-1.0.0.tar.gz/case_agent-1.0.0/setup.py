from setuptools import setup, find_packages

setup(
    name="case-agent",
    version="1.0.0",
    description="Generate agentic case-profile.yaml files for client-specific deployments. Contributor-safe agent framework for diagnostics and delivery",
    author="QUEST",
    author_email="quest@systems.dev",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "case-agent=case_agent.cli:main"
        ]
    },
    install_requires=["PyYAML"],
    include_package_data=True,
    license="None",
    python_requires=">=3.7"
)
