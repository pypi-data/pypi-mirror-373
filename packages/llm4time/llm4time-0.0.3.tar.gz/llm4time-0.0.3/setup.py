from setuptools import setup, find_packages

with open("README.md", "r") as arq:
  readme = arq.read()

setup(name='llm4time',
      version='0.0.3',
      license='MIT License',
      author='Zairo Bastos',
      long_description=readme,
      long_description_content_type="text/markdown",
      author_email='zairobastos@gmail.com',
      keywords=['forecast', 'llm'],
      description='Um pacote para previsão de séries temporais usando modelos de linguagem.',
      packages=find_packages(),
      install_requires=[
          "lmstudio==1.3.0",
          "numpy==2.2.5",
          "openai==1.86.0",
          "pandas==2.2.3",
          "permetrics==2.0.0",
          "plotly==6.1.0",
          "python-dotenv==1.1.0",
          "scikit-learn==1.7.1",
          "scipy==1.15.3",
          "setuptools==80.9.0",
          "tiktoken==0.11.0"
      ],
      extras_require={
          'streamlit': [
              "streamlit==1.45.1",
              "st-pages==1.0.1",
              "streamlit-option-menu==0.4.0"
          ]
      })
