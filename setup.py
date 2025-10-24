"""
LangGraph 智能客服系统 - 安装配置
"""
from setuptools import setup, find_packages

setup(
    name="langraph-customer-service",
    version="1.0.0",
    description="基于LangGraph和硅基流动API的生产级智能客服系统",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "langgraph==0.2.45",
        "langchain==0.3.7",
        "langchain-openai==0.2.5",
        "langchain-community==0.3.5",
        "faiss-cpu==1.8.0",
        "sentence-transformers==3.3.1",
        "python-dotenv==1.0.1",
        "pydantic==2.10.1",
        "pydantic-settings==2.6.1",
        "loguru==0.7.2",
        "pandas==2.2.3",
        "numpy==1.26.4",
        "fastapi==0.115.4",
        "uvicorn==0.32.0",
    ],
    entry_points={
        "console_scripts": [
            "customer-service=langraph_customer_service.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

