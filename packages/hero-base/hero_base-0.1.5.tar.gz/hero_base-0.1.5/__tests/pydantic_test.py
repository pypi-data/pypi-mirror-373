import json
from typing import Dict, Any, List, Optional


from pydantic import BaseModel, Field

class Body(BaseModel):
    param2: int = Field(description="参数2描述", default=0)
    param3: int = Field(description="参数3描述")

class MyTool(BaseModel):
    """对工具的描述"""
    param1: int = Field(description="参数1描述")
    body: Body = Field(description="body参数描述")

def model_to_schema(model: type[BaseModel]) -> dict:
    """将Pydantic模型转换为OpenAPI schema"""
    return model.model_json_schema()

json_schema = model_to_schema(MyTool)
print(json_schema)

json_str = json.dumps(json_schema, indent=4, ensure_ascii=False)
print(json_str)

tool_demo = MyTool(param1=1, body=Body(param2=2, param3=3))

class OpenAITool(BaseModel):
    """OpenAI Function Calling 工具包装器"""
    type: str = "function"
    function: Dict[str, Any]

class OpenAIToolBuilder:
    """构建OpenAI Function Calling工具的构建器"""
    
    @staticmethod
    def from_pydantic_model(
        model_class: type[BaseModel],
        name: str,
        description: Optional[str] = None
    ) -> OpenAITool:
        """
        从Pydantic模型创建OpenAI工具
        
        Args:
            model_class: Pydantic模型类
            name: 工具名称
            description: 工具描述，如果为None则使用模型的docstring
        
        Returns:
            OpenAITool实例
        """
        # 获取模型的schema
        schema = model_class.model_json_schema()
        
        # 使用模型的docstring作为描述（如果未提供）
        if description is None:
            description = model_class.__doc__ or f"使用{name}工具"
        
        # 构建function定义
        function_def = {
            "name": name,
            "description": description,
            "parameters": schema,
            "strict": True,
        }
        
        return OpenAITool(
            type="function",
            function=function_def
        )

# 使用示例
def create_openai_tools() -> List[OpenAITool]:
    """创建OpenAI function calling格式的工具列表"""
    tools = []
    
    # 将MyTool转换为OpenAI工具
    my_tool = OpenAIToolBuilder.from_pydantic_model(
        model_class=MyTool,
        name="my_tool",
        description="这是一个自定义工具，用于处理特定任务"
    )
    tools.append(my_tool)
    
    return tools

# 演示如何使用
if __name__ == "__main__":
    # 创建OpenAI工具
    openai_tools = create_openai_tools()
    
    # 转换为JSON格式（可以直接用作OpenAI API的tools参数）
    tools_json = [tool.model_dump() for tool in openai_tools]
    
    print("OpenAI Function Calling 格式的工具:")
    print(json.dumps(tools_json, indent=2, ensure_ascii=False))
    
    # 也可以单独获取某个工具
    my_tool = openai_tools[0]
    print(f"\n工具名称: {my_tool.function['name']}")
    print(f"工具描述: {my_tool.function['description']}")