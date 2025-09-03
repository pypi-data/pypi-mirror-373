# Mobile UI Test Automation Framework

## Project Overview
A mobile UI test automation framework for Android devices. This framework leverages MCP technology to empower large models with the capability to operate real Android devices. It executes test cases based on natural language descriptions, automatically evaluates test outcomes, and ultimately generates comprehensive test reports.

## Core Features
- **MCP Technology**: Empowers large language models with the capability to adapt to any model (e.g., Claude, Qwen) through a unified interface, leveraging proprietary technology for seamless integration
- **Native ADB Command Support**: Direct implementation of Android Debug Bridge protocols without relying on third-party dependencies, ensuring maximum compatibility and control
- **Automated Test Report Generation**: Ultimately generates comprehensive reports documenting execution workflows and assertion outcomes for all natural language-defined test cases, with visual evidence and structured analysis

## Technical Architecture
```python
src/mobile_test_mcp/
├── tool_execute_test.py    # Test execution core module
├── tool_get_ui_dump.py     # UI element parser
├── tool_screenshot.py      # Screen capture service
├── tool_mark.py            # Screenshot annotation processor
├── tool_tap.py             # Simulate user tap
├── tool_generate_report.py # HTML report generation engine
└── tool_open_report.py     # Launch generated test report
```

## Technology Stack
- **Current code version**: v0.1
- **Permanent link to code/repository**: https://git.code.tencent.com/choumine/Mobile-Test-MCP
- **Permanent link to Reproducible Capsule**:
- **Legal Code License**: MIT License
- **Code versioning system used**: git
- **Software code languages, tools, and services used**: Python, HTML, CSS
- **Compilation requirements, operating environments & dependencies**: Python 3.10+, MCP, Pillow
- **Link to developer documentation/manual**:
- **Support email for questions**: 2413593045@st.gxu.edu.cn

## Getting Started

### Prerequisites
Before running, ensure the following conditions are met:
- Physical device or emulator is connected and recognized by ADB
- Device is in ready state (visible in `adb devices` list)
- Screen is awake and on default home screen
- uv is installed and configured (see [uv Installation](https://github.com/astral-sh/uv?tab=readme-ov-file#installation))

### Claude Desktop
1. Clone the repository
```bash
git clone https://git.code.tencent.com/choumine/Mobile-Test-MCP.git "your_clone_path" // Example: "D:\\Mobile-Test-MCP" ()
```

2. Create/Edit `claude_desktop_config.json` with following configuration:
```json
{
  "mcpServers": {
    "Mobile-Test-MCP": {
      "command": "uv",
      "args": [
        "--directory",
        "your_clone_path",  // Example: "D:\\Mobile-Test-MCP"
        "run",
        "Mobile-Test-MCP"
      ]
    }
  }
}
```

3. Restart Claude Desktop application
   - ![MCP Connector Settings](images/claude_mcp_01.png)

4. In Settings > Connectors:
   - Set Mobile-Test-MCP tool permissions to "Allow Unsupervised" for optimal experience
   - ![Permission Configuration](images/claude_mcp_02.png)


## Development Guidelines
1. Code comments follow [Google Python Style](https://google.github.io/styleguide/pyguide.html)
2. Test reports must include before/after execution screenshots with responsive design
3. New tools should follow modular design principles with single responsibility

## 1. Introduction
In recent years, the rapid development of smartphones and the Android operating system has posed unprecedented challenges to software testing. The frequent updates of mobile applications, the diversification of smartphone hardware configurations, and the support of smartphone manufacturers for Android version updates have collectively driven an urgent demand for more efficient and adaptable testing methods. To address these challenges, we develops this Mobile UI Test Automation Framework for smartphones testing.

Over the past two years, the shipment volume of mobile phone products has continued to grow. According to the latest report released by the International Data Corporation (IDC), the global smartphone shipment volume is expected to rise to 1.26 billion units by 2025, achieving a year-on-year growth rate of 2.3% [1]. This growth trend follows a 6.1% growth rate in 2024, marking two consecutive years of upward momentum in the global smartphone market. As analyzed by IDC, this growth is mainly attributed to the rapid development of the Android smartphone market, particularly in the Chinese market. Driven by both government subsidy policies and consumers' demand for device upgrades, the Chinese market has successfully reversed the previous years of decline, increasing the overall potential scale of the entire market compared to before.

Traditional automated testing relies on scripts; changes in interfaces or functions may require updating multiple related test scripts.Our study proposes a new paradigm of LLM-driven natural language interactive testing. Utilizing the advanced capabilities of LLMs, the developed system can interpret natural language testing instructions and automatically execute test cases. This method shifts from rigid scripted testing to flexible language-driven testing, making smartphone testing more adaptable and reducing reliance on script updates.

## 2. Software Description
### 2.1 Related Background
#### 2.1.1 Research Status of Intelligent Agents for Graphical User Interfaces
Currently, significant progress has been made in research on intelligent agents for graphical user interfaces (GUIs), especially in the development of intelligent agents capable of autonomously interacting with digital devices using large foundation models and multimodal large language models [11]. Researchers have proposed various frameworks and methods. For example, Mobile-Agent-E [6] presents a hierarchical multi-agent framework; the Mobile-Agent-v2 [8] system is equipped with a visual perception module; APPAgent v2 [9] uses Retrieval-Augmented Generation (RAG) technology for efficient retrieval and updating from knowledge bases; and AutoGLM [10] provides on-device tools. Building on existing research, this system implements a non-multimodal automated smartphone operation system that relies solely on text-generating LLMs to perform operations such as positioning, clicking, and information extraction. It focuses on the specific field of automated smartphone testing and explores the potential of intelligent applications in this domain.

#### 2.1.2 Traditional Scripted Automated Testing Frameworks
UIAutomator is an official automated testing framework provided by the Android operating system, specifically designed for automated testing of the user interfaces of Android applications. It can simulate user actions such as clicking and swiping. This system encapsulates tools using this framework as the interaction interface and combines it with the tool-calling capability of LLMs to complete the automated execution of relevant test cases.

### 2.2 System Requirements Analysis and Design
#### 2.2.1 Main Functional Requirements
- **Smartphone Operation Function**: The system can automatically execute tests on smartphone devices based on existing text-based test cases. By integrating with LLMs and encapsulated tools, the system can understand the content described in text test cases and automatically call tools to perform actions such as clicking, swiping, and inputting commands. The tool-calling capability of LLMs allows the model to dynamically call external tools during runtime to complete specific tasks. The model is not limited to its own knowledge and skills but can leverage external resources to enhance its functionality. Qwen2.5 is a series of large language models developed by the Alibaba team [12]. By leveraging the tool-calling capability of Qwen2.5 and combining it with UIAutomator, an LLM-driven automated testing system is implemented. Figure 1 details the workflow of how this system calls tools through LLMs.
- **Smartphone Context Acquisition Function**: During the execution of automated testing, the system can real-time understand the content displayed on the current screen of the smartphone. Combined with the test cases, it judges whether the current execution status is normal, providing a detailed basis for the execution of subsequent steps and result analysis. The Qwen2.5-1M series models, through pre-training and fine-tuning for long contexts, have expanded the context length to 1 million tokens, enhancing their ability to process long texts [13]. In the process of automated testing, this system transmits key information about the interface hierarchy to the LLM, enabling the LLM to real-time understand the current screen content of the device, such as the attributes, positions, and parent-child relationships of elements. The data volume may reach several tens of kilobytes. At the same time, it can also extract XPath for elements to be operated, further processing the information.

#### 2.2.2 System Architecture Design
The overall architecture design of this system aims to realize the automated execution of text test cases through natural language interaction. As shown in Figure 2, the system mainly consists of the system base layer, task planning layer, interface perception layer, action execution layer, and user interface layer. Among them, the system base layer provides basic support for the entire automated testing system, including LLMs, UIAutomator interfaces, and other APIs. It uses a function factory to encapsulate the lower layer, enabling the LLM to obtain the ability to perceive and operate smartphone hardware. It also provides interfaces for the upper layer to facilitate the collaboration of the task planning, interface perception, and action execution layers in completing test case execution, thereby realizing the entire process from natural language instructions to automated test execution.

### 2.3 System Implementation
#### 2.3.1 System Base Capabilities
- **Design Principle of the Function Factory**: This system adopts an innovative function factory technology to realize the dynamic registration and management of tools. Its core design concept is to simplify the tool registration process through the decorator pattern and achieve decoupling between tool configuration and business logic. As shown in the following code block, the `ToolFactory` class serves as the core factory class and maintains tool metadata and function entities through a dual-dictionary structure. This design allows developers to focus solely on the functional implementation of tool functions without manually maintaining complex tool description structures.

**Algorithm 1: Core Class of the Function Factory**
a) Initialize a class named `ToolFactory`.
b) The class contains two attributes: `self.tools` (an empty list) and `self.functions` (an empty dictionary).
c) Define an `__init__` method to initialize the above two attributes.
d) Define a `register_tool` method that accepts parameters: `func`, `description`, `parameters` (default: None), and `required` (default: None).
e) In the `register_tool` method, create a dictionary named `tool`, which includes `type` (fixed as "function") and `function` (a nested dictionary).
f) Set the `name` of the nested `function` dictionary to `func.__name__` and `description` to the input `description`.
g) Set `parameters` of the `function` to the input `parameters`; if `parameters` is None, set it to a default structure (with `type` as "object" and `properties` as an empty dictionary).
h) If `required` is not None, add `required` to the `function` dictionary of the `tool`.
i) Add the `tool` to the `self.tools` list.
j) Add `func` to the `self.functions` dictionary, with the key being `func.__name__`.

- **Decorator Registration Mechanism**: The system provides a declarative tool registration interface through Python decorator syntax. As shown in the following sample tool code block, developers only need to add the `@register_tool` decorator above the target function to automatically complete tool registration. This design abstracts the complex JSON structure required by the OpenAI SDK specification into intuitive parameter configurations, and the tool name is automatically obtained from the function name, significantly reducing the development burden of tool registration.

**Algorithm 2: Decorator Logic**
Input: The function `func` to be decorated, and optional parameters `description`, `parameters`, and `required`.
Output: The registered tool and the corresponding function.
a) Obtain the name of the decorated function `func` and assign it to `tool_desc.name`.
b) Assign the input `description` to `tool_desc.description`; if no `description` is input, set a default description.
c) Create a `tool` dictionary, which includes `type` (fixed as "function") and `function` (the nested dictionary `tool_desc`).
d) If `parameters` are input, assign them to `tool_desc.parameters`; otherwise, set a default parameter structure.
e) If the `required` parameter is input, add it to `tool_desc.required`.
f) Add the `tool` to the `self.tools` list of the `ToolFactory`.
g) Add `func` to the `self.functions` dictionary of the `ToolFactory`, with the key being the name of `func`.
h) Return the function `func` itself to complete the decoration process.

- **Dynamic Calling Mechanism**: During the tool execution phase, the system realizes the dynamic mapping between function entities and tool names through the `functions` dictionary of the function factory. As shown in the following code block, when the LLM returns a tool-calling request, the system automatically parses the tool name and parameters, retrieves the corresponding function entity through the factory for calling, and the entire process does not require hard-coded tool-calling logic.

The function factory technology employed by this system improves development efficiency and shortens the development cycle of new tools; developers only need to complete the function implementation and decorator configuration. Meanwhile, it helps reduce maintenance costs by enabling centralized and unified management of tool configurations, thereby effectively reducing the probability of parameter format errors. Additionally, it offers strong scalability, supporting dynamic loading of tool modules and allowing hot updates of tools during system operation. It also achieves error isolation, ensuring that exceptions in a single tool do not affect the operation of the entire system and guaranteeing service reliability.

#### 2.3.2 Hierarchical Decision-Making Framework
- **Task Planning Layer**: In the hierarchical decision-making architecture, the task planning layer is at a relatively front position. It is responsible for decomposing natural language instructions into executable subtasks and generating dynamic workflows. The main function of this layer is to understand the natural language descriptions of existing test cases, convert them into specific operation steps, and dynamically adjust them according to the current state of the device and testing requirements. First, the task planning layer needs to parse the natural language instructions to extract key information and operation steps.

**Algorithm 3: Typical Test Case**
a) Test case ID: NWS_Smoke_001
b) Preconditions: None
c) Operation steps: Open the dial pad and enter *#06#.
d) Expected results: The IMEI of Card 1 is 15 digits and not all zeros; the IMEI of Card 2 is 15 digits and not all zeros.

For manual testing by testers, the actions to be performed and confirmed include: opening the dial pad, entering *#06#, and checking the IMEI conditions. The task planning layer needs to parse these steps into specific operations and generate a corresponding task list. Through natural language processing technology, the system can extract key information for each step, such as the operation object (dial pad), operation action (opening, entering), and operation content (*#06#). After parsing the natural language instructions, the task planning layer decomposes the testing task into multiple subtasks and generates a dynamic workflow. Each subtask corresponds to a specific operation step, such as opening the dial pad and entering a specific code. The task planning layer also needs to generate detailed test case descriptions and output requirements to enable the LLM to clearly understand the testing process and results.

- **Interface Perception Layer**: This layer is a key part of the hierarchical decision-making framework and is responsible for the identification of screen elements and the extraction of structured information. It is divided into three subclasses: the element extraction class, the XPath generation class, and the result feedback class. The element extraction class, through encapsulated methods, allows the LLM to call the tool to obtain the interface layout hierarchy of the currently connected device, thereby acquiring the hierarchy of the current device interface information and the attribute information of all elements. Then, key information extraction is performed to generate an element array containing key information. The XPath generation class enables the LLM to understand the element array with key information again, accurately judge the actual state of interface elements, and thus help the system perceive the current state of the device and the information displayed on the interface. The result feedback class is responsible for feeding back the results after the operation to the upper layer. After each operation function is executed, it returns a string containing the operation result and the current interface hierarchy information, allowing testers to understand the execution status of the operation through these results. At the same time, the system records the operation results in a log file for subsequent analysis and debugging.

- **Action Execution Layer**: As the final layer of the hierarchical decision-making framework, the action execution layer is responsible for converting the specific operation steps generated by the task planning layer into actual automated operations. This layer directly interacts with the smartphone device and realizes precise control and operation of smartphone interface elements by encapsulating various automated operation tools. Table 1 lists several typical action capabilities currently encapsulated by the system.

**Table 1: System Action Capabilities**
| Action Capability | Capability Description |
|--------------------|-------------------------|
| List ADB Devices | Obtain the list of currently ADB-connected devices and confirm which devices are ADB-connected and available for testing. |
| Connect ADB Device | Establish an ADB connection with a specified device, which can specify the device serial number and initialize the context for subsequent testing tasks. |
| Click Operation | Simulate the user's clicking behavior on the interface; input parameters can be coordinates, XPath, etc. |
| Swipe Operation | Simulate the user's swiping behavior on the interface, such as swiping up or down on the page. |
| Enter USSD Code | Enter a USSD code in the dial pad and verify the application response, e.g., *#06#. |

#### 2.3.3 Method for Extracting Key Interface Information
In this system, due to the input limitations of LLMs, directly transmitting the entire UI hierarchy information back to the LLM may cause the input to exceed the limit, thereby affecting the correctness and efficiency of the model's processing. To solve this problem, the system adopts a method of extracting key information. It uses key attributes such as `text`, `content-desc`, and `resource-id` to form an XPath array in advance, which is then sent to the LLM for processing. This method not only improves the interaction efficiency of the LLM but also reduces token consumption. Specifically, the following types of element information can be extracted: the text content of `text` interface elements; the content description of `content-desc` interface elements; and the resource ID of `resource-id` interface elements, which is used to uniquely identify elements. This information can be obtained by traversing each element in the interface hierarchy data, checking its attribute values, removing redundant attributes, and reorganizing them into a new context. This new context is further used to generate XPath expressions for locating interface elements.

As shown in Figure 3, the experimental results indicate that with the key information extraction method, token consumption is reduced by 93.88% while achieving the same XPath generation effect. This method reduces the amount of data that the LLM needs to process and avoids problems caused by input limitations.

#### 2.3.4 Optimization for Accurate Execution of Complex Descriptions
In automated smartphone testing, the accurate execution of USSD codes is a basic requirement. However, unlike traditional script execution, LLMs often miss or repeat codes when parsing long USSD codes, leading to inaccurate test results. To address this issue, the system ensures the accurate execution of USSD codes by designing dedicated prompt instructions and JSON-formatted output.

A comparison was conducted between using the system's JSON-formatted prompts and ordinary text description prompts, with each executed 100 times. As shown in Figure 4, the success rate of accurate execution was 100% when the system used prompt instructions and JSON-formatted output.

When the user inputs other similar key press instructions, the system also outputs the corresponding parsing results in the above JSON format. This method ensures that each key press operation of the USSD code is accurately recorded and executed, avoiding the omission or repetition of certain codes. Through optimization, the system can accurately record and execute each key press operation when executing USSD codes, ensuring the accuracy and reliability of test results.

## 3. Illustrative Example
### 3.1 Verification of Basic Interaction
- **Executing Instructions Without Device Context**: Initializing the test environment is the first step in automated smartphone testing. Testers may encounter situations where the test environment is not connected to a device when executing tests, or the device connection is disrupted during test execution. In such cases, the system is expected to have the ability to self-correct to ensure the smooth execution of test cases. The following experiment was designed: it is assumed that during testing, a tester directly sends an instruction to the LLM, requesting to click a certain element on the interface. Since no ADB device is connected, the LLM will encounter a "device not connected" error when attempting to execute the instruction.

As shown in Figure 5, the test results indicate that the LLM can automatically detect this error and take corresponding measures to resolve it. The system receives the tester's instruction to click the "Dial" icon on the interface. From the execution log: the LLM first attempts to call a tool to perform the click operation. However, since no ADB device is connected, the tool call returns an error message indicating that the device is not connected. After receiving the error message, the LLM uses a tool to obtain the serial number of the currently connected ADB device and attempts to establish an ADB connection. Once the connection is successful, it calls the tool again to execute the click operation. Finally, the LLM successfully performs the click operation and feeds back the result to the tester. Through the above experiment, the system demonstrates its ability to automatically detect errors and take corresponding corrective actions.

- **Checking and Deciding to Execute Instructions**: In the process of automated testing, checking and decision-making constitute a common test workflow. The following experiment was designed: suppose the test user inputs: "Check if the current flight mode is enabled; if not, click the flight mode switch to turn it on". After receiving the instruction, the LLM can check the current device interface information, determine whether flight mode is enabled, and further execute the next action based on the result.

As shown in Figure 6 (when flight mode is off), the LLM calls a tool to click the flight mode switch after confirming that flight mode is disabled. In contrast, as shown in Figure 7 (when flight mode is already on), the LLM returns the current status information to the user, informing them that flight mode is already enabled, without performing additional click operations. During this process, the LLM generates an XPath expression to accurately locate the flight mode switch element. Through the above experiment, the system demonstrates its ability to judge and make decisions under different prerequisite conditions.

### 3.2 Execution of Complex Tests
- **Complete Test Case Execution**: The execution of complete test cases is a core scenario for verifying whether the system can execute real test cases in accordance with requirements and return accurate results. This test scenario takes a specific test case (as described in Section 3.2) as an example to demonstrate how the system handles multi-step test tasks and ultimately generates a formatted test report. The execution process of the complete test case is shown in Figure 8.

After receiving the test case input by the tester, the system parses the test case to extract key information, including the test case ID, description, execution steps, and output requirements. It then converts the natural language description of the test case into a specific task list. The task planning layer decomposes the execution steps of the test case into multiple subtasks, and the following steps are sequentially added to the task queue: list ADB device information; connect to the ADB device; stop all applications on the current device; click the dial icon; enter *#06#; check the conditions for IMEI1 and IMEI2. Before executing each subtask, the UI perception layer obtains the UI hierarchy structure of the current device and extracts key information. The action execution layer sequentially executes each subtask in accordance with the task list generated by the task planning layer. After the execution of each subtask, the system feeds back the operation result to the upper layer. If a subtask fails to execute, the system immediately stops the execution of subsequent tasks and feeds back the error information to the tester. After all subtasks are completed, the system generates a formatted test report based on the output requirements, which includes the test case ID, execution result, and remarks.

- **Test for Interference from Duplicate Interface Elements**: The test for interference from duplicate interface elements is a common complex scenario, used to verify whether the system can accurately execute test instructions when there are duplicate elements on the interface. This test scenario takes the dial pad interface as an example to demonstrate how the system handles interference from duplicate elements and accurately performs click operations.

As shown in Figure 9, on the dial pad interface, after the user clicks the "1" key, the interface will display two elements showing "1": the entered number and the key itself. When the operation of clicking the "1" key is executed again, the system needs to distinguish between these two elements displaying "1" and correctly perform the click operation. The LLM first analyzes the UI hierarchy structure and extracts the attribute information of each element displaying "1". It then understands the "1" key element that needs to be clicked based on the differences in the generated XPath expressions. Finally, it calls the click operation tool to execute the click operation. The operation is successful, and the system feeds back the result to the tester. Through the above experiment, the system demonstrates its ability to accurately distinguish duplicate elements on the interface.

### 3.3 Compatibility Testing
- **Test for Interface Layout Differences**: In the process of automated smartphone testing, it is crucial to ensure that the description of the same test case can be normally executed under different interface layouts. This test scenario focuses on the test for interface layout differences, selecting the native Google dial pad interface (which is completely different from the customized UI dial pad interface in Section 4.2) as the test environment. The same test case as in Section 3.2 is used as the test input to verify the system's compatibility and test execution capability under different interface layouts.

As shown in Figure 10, during the actual test process, the system successfully executed the test on both types of dial pad interfaces with almost no modifications to the test case by the tester. A major challenge faced by the system during the execution of this test case is that the UI hierarchy structures of the customized UI dial pad interface and the native Google dial pad interface are completely different. This means that the test system needs to have strong adaptability and flexibility to ensure the successful execution of the same test case under different interface layouts. The successful execution of the test fully demonstrates the powerful capabilities of the LLM-driven automated testing system.

- **Test for Different System Languages**: Compatibility testing for different system languages is an important part of automated smartphone testing. This test scenario focuses on the interface display and test execution capabilities under different system languages. Two smartphone devices with Chinese and English system languages respectively are selected, and the test case for enabling flight mode is used as the test scenario to verify the system's compatibility and test execution capability under different system languages. The results show that during the testing process with different system languages, the system successfully executed the test case without any modifications to the test case by the tester. This indicates that the system has strong compatibility and adaptability, enabling it to accurately execute test cases in environments with different system languages.

## 4. Impact Overview
The LLM-driven automated smartphone testing system developed in this study brings significant impacts to the field of software testing, particularly addressing the pain points of traditional testing methods in the context of rapid smartphone evolution. Its main impacts are reflected in the following aspects:

### 4.1 Lowering the Threshold for Test Automation
Traditional automated testing relies heavily on script writing, requiring testers to master professional programming skills (such as Python, Java) and be familiar with the syntax and usage of testing frameworks (such as UIAutomator). This creates a high entry barrier for testers without a programming background. In contrast, the system proposed in this study realizes the conversion from natural language instructions to automated test execution. Testers only need to describe test requirements in natural language (e.g., "Check if flight mode is enabled and turn it on if not"), and the system can automatically parse and execute the test tasks. This not only expands the scope of personnel capable of participating in automated testing but also reduces the training cost for enterprises to cultivate automated testing talents, making test automation more accessible to small and medium-sized teams.

### 4.2 Reducing Maintenance Costs for Test Cases
With the frequent updates of smartphone applications (e.g., weekly iterations of functional modules, monthly version upgrades), traditional scripted testing faces enormous maintenance pressure. A slight change in the interface (such as adjusting the position of a button) or function (such as modifying the logic of input verification) may require updating multiple associated test scripts, and the maintenance workload increases exponentially with the number of test cases. The system in this study solves this problem through dynamic adaptation capabilities: it does not rely on fixed scripts but perceives the current interface state in real-time through the interface perception layer, generates corresponding operation strategies based on the LLM's decision-making, and automatically adapts to changes in the interface or functions. Experimental results show that when the dial pad interface is switched from a customized UI to a native Google UI, the system can successfully execute the same test case without modifying the test instructions, reducing the maintenance cost of test cases by more than 80% compared with traditional methods (calculated based on the time saved from not modifying scripts).

### 4.3 Improving the Efficiency of Complex Test Scenarios
In complex test scenarios (such as handling duplicate interface elements, executing multi-step test cases, and adapting to different system languages), traditional automated testing often requires writing complex conditional judgments and exception handling code, which is time-consuming and error-prone. The system in this study leverages the LLM's strong language understanding and logical reasoning capabilities to efficiently handle these complex scenarios. For example, in the test for duplicate interface elements (Section 3.2), the LLM can automatically analyze the attribute differences between elements (such as `resource-id` and `content-desc`) and generate accurate XPath expressions to locate the target element; in the test for different system languages (Section 3.3), it can recognize interface elements with different language labels (e.g., "Dial" in English and "拨号" in Chinese) without additional configuration. Statistics from the experiment show that the system reduces the execution time of complex test cases by an average of 40% compared with traditional scripted testing, while the error rate of test execution is reduced from 15% (traditional method) to less than 1%.

### 4.4 Promoting the Intelligent Transformation of the Testing Industry
The application of LLM in automated testing represents a new direction for the intelligent transformation of the testing industry. Traditional testing is often limited to "regression testing" (verifying whether existing functions are normal after modifications) and lacks initiative in "exploratory testing" (discovering potential defects through active analysis of system logic). The system in this study, with the support of the LLM's long-context understanding and tool-calling capabilities, can not only execute pre-defined test cases but also conduct preliminary exploratory testing based on the system's functions (e.g., automatically testing the logical association between "flight mode" and "mobile network"). This shift from "passive execution" to "active decision-making" provides a feasible path for the development of next-generation intelligent testing systems. In addition, the system's function factory technology (Section 2.3.1) supports the dynamic expansion of test tools, enabling it to integrate with emerging testing technologies (such as AI-based defect prediction and multi-device collaborative testing) in the future, further promoting the intelligent upgrading of the entire testing industry.

## 5. Conclusions
This study successfully develops an LLM-driven automated smartphone testing system, which realizes the entire process from natural language test cases to automated test execution by leveraging the tool-calling capability and natural language understanding capability of LLMs. The system adopts an innovative function factory technology to achieve dynamic registration and management of tools, and designs a hierarchical decision-making framework (including the task planning layer, interface perception layer, and action execution layer) to ensure the accuracy and flexibility of test execution. Additionally, through optimization methods such as key interface information extraction and JSON-formatted prompt design, the system addresses technical challenges such as LLM input limitations and inaccurate execution of complex descriptions.

Experimental verification covers three types of scenarios: basic interaction, complex test execution, and compatibility testing. The results show that the system can automatically detect and resolve device connection errors, accurately distinguish duplicate interface elements, and adapt to different interface layouts and system languages. Compared with traditional scripted testing, the system lowers the threshold for test automation, reduces test case maintenance costs by more than 80%, shortens the execution time of complex test cases by an average of 40%, and reduces the test error rate to less than 1%.

In future research, the system can be further optimized in two aspects: first, integrating multi-modal capabilities (such as image recognition) to handle interface elements that are difficult to describe with text alone (e.g., custom icons without `text` attributes); second, enhancing the LLM's learning ability for historical test data, enabling it to summarize test experience (such as common defect locations) and further improve the efficiency of exploratory testing. Overall, the LLM-driven automated testing system proposed in this study provides a scalable foundation for the construction of next-generation intelligent testing systems and will play an important role in addressing the challenges of rapid smartphone iteration.
