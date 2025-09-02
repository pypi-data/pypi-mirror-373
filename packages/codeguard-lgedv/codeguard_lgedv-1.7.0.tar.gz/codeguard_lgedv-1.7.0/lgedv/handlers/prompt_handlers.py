"""
Prompt handlers for MCP server operations
Xử lý các MCP prompts cho phân tích code
"""
import os
from typing import Dict
from mcp import types
from lgedv.prompts.prompt_templates import PromptTemplates
from lgedv.analyzers.memory_analyzer import MemoryAnalyzer
from lgedv.modules.config import get_src_dir, setup_logging

logger = setup_logging()

class PromptHandler:
    """Handler cho các MCP prompts"""
    
    def __init__(self):
        self.templates = PromptTemplates()
    
    async def handle_prompt(self, name: str, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Route và xử lý prompt calls
        
        Args:
            name: Tên prompt
            arguments: Arguments cho prompt
            
        Returns:
            GetPromptResult
        """
        logger.info(f"Prompt called: {name} with arguments: {arguments}")
        
        try:
            if name == "check_lgedv":
                return await self._handle_lgedv_check()
            elif name == "check_misra":
                return await self._handle_misra_check()
            elif name == "check_certcpp":
                return await self._handle_certcpp_check()
            elif name == "check_custom":
                return await self._handle_custom_check()
            elif name == "check_races":
                return await self._handle_race_condition_analysis(arguments)
            elif name == "check_leaks":
                return await self._handle_memory_leak_analysis(arguments)
            elif name == "check_resources":
                return await self._handle_resource_leak_analysis(arguments)
            elif name == "get_code_context":
                return await self._handle_code_context()  
            elif name == "reset_analysis":
                return await self._handle_reset_analysis_prompt(arguments)
            if name == "reset_mem_check":
                return await self._handle_reset_mem_check_prompt(arguments)
            if name == "reset_resource_check":
                return await self._handle_reset_resource_check_prompt(arguments)
            if name == "reset_race_check":
                return await self._handle_reset_race_check_prompt(arguments)
            else:
                raise ValueError(f"Unknown prompt: {name}")
                
        except Exception as e:
            logger.exception(f"Error in prompt handler for {name}: {e}")
            raise
    
    async def _handle_lgedv_check(self) -> types.GetPromptResult:
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc LGEDV cho phần mềm ô tô.\n"
                "Nếu chưa có file rule, hãy gọi fetch_lgedv_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc LGEDV mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm LGEDV\n"
                "- Ghi rõ số hiệu rule (VD: LGEDV_CRCL_0001, MISRA Rule 8-4-3, DCL50-CPP, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"                
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"             
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_lgedv_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for LGEDV rule on current file.",
        )
        logger.info("LGEDV check prompt completed")
        return result
    
    async def _handle_misra_check(self) -> types.GetPromptResult:
        """Handle MISRA code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc MISRA C++ 2008 cho phần mềm an toàn.\n"
                "Nếu chưa có file rule, hãy gọi fetch_misra_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc MISRA mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm MISRA\n"
                "- Ghi rõ số hiệu rule (VD: MISRA Rule 8-4-3, LGEDV_CRCL_0001, DCL50-CPP, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_misra_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for MISRA rule on current file.",
        )
        logger.info("MISRA check prompt completed")
        return result
    
    async def _handle_certcpp_check(self) -> types.GetPromptResult:
        """Handle CERT C++ code checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc CERT C++ Secure Coding Standard.\n"
                "Nếu chưa có file rule, hãy gọi fetch_certcpp_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc CERT C++ mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm CERT\n"
                "- Ghi rõ số hiệu rule (VD: DCL50-CPP, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"               
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_certcpp_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for CERT C++ rule on current file.",
        )
        logger.info("CERT C++ check prompt completed")
        return result
    
    async def _handle_custom_check(self) -> types.GetPromptResult:
        """Handle Custom rule checking prompt"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là chuyên gia phân tích tĩnh C++. Hãy phân tích file hiện tại để phát hiện vi phạm các quy tắc custom dưới đây.\n"
                "Nếu chưa có file rule, hãy gọi fetch_custom_rule từ MCP server.\n"
                "Luôn sử dụng bộ quy tắc custom mới nhất vừa fetch để phân tích, không dùng rule cũ hoặc built-in.\n"
                "Hãy ghi rõ bộ rule nào đang dùng trong báo cáo.\n\n"
                "**YÊU CẦU PHÂN TÍCH:**\n"
                "- Tìm TẤT CẢ vi phạm quy tắc trên\n"
                "- Tập trung vào vi phạm custom rule\n"
                "- Ghi rõ số hiệu rule (VD: CUSTOM-001, MISRA Rule 8-4-3, LGEDV_CRCL_0001, RS-001)\n"
                "- Kiểm tra mọi dòng code, kể cả unreachable, dead code, return sớm, magic number\n"
                "- Kiểm tra mọi điểm acquire/release resource, mọi exit point, mọi function/method\n"
                "- Đưa ra code fix cụ thể cho từng lỗi\n"
                "- Ghi số dòng code gốc trong báo cáo\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi lỗi:\n"
                "## 🚨 Vấn đề [#]: [Mô tả ngắn]\n\n"
                "**Rule vi phạm:** [SỐ HIỆU] - [Mô tả rule]\n\n"
                "**Vị trí:** [tên hàm hoặc global/unknown]\n\n"
                "**Mức độ:** [Critical/High/Medium/Low]\n\n"
                "**Code hiện tại:**\n"
                "```cpp\n[code lỗi]\n```\n"
                "**Code đã sửa:**\n"
                "```cpp\n[code đúng]\n```\n"
                "**Giải thích:** [Vì sao vi phạm và cách sửa]\n\n"         
                "**Lưu ý:** Nếu cần toàn bộ file code đã fix, hãy yêu cầu rõ ràng."
            )
        else:
            prompt = self.templates.get_custom_analysis_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for Custom rule on current file.",
        )
        logger.info("Custom check prompt completed")
        return result
    
    async def _handle_race_condition_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle race condition analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_src_dir()
        logger.info(f"[check_races] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_detect_races({})
           
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Race condition analysis (full result)",
                )
                logger.info("Race condition analysis prompt (fallback style) completed")
                return result
            else:
                logger.warning("No result from tool")
                return None
            
        except Exception as e:
            logger.error(f"Error in race condition analysis: {e}")
            return None
            
    async def _handle_memory_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle memory leak analysis prompt - always use fallback-style prompt with findings if available"""
        dir_path = get_src_dir()
        logger.info(f"[check_leaks] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            tool_result = await tool_handler._handle_memory_analysis({"dir_path": dir_path})
            
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Memory leak analysis (full result)",
                )
                logger.info("Memory leak analysis prompt")
                return result
            else:
                logger.warning("No result from tool for memory leak analysis")
                return None
        except Exception as e:
            logger.error(f"Error in memory leak analysis: {e}")
            return None
           
       
    async def _handle_resource_leak_analysis(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """Handle resource leak analysis prompt - always use fallback-style prompt with findings if available, now with line numbers"""
        dir_path = get_src_dir()
        logger.info(f"[check_resources] Using src_dir: {dir_path}")
        try:
            from lgedv.handlers.tool_handlers import ToolHandler
            tool_handler = ToolHandler()
            # Also append the original findings text for reference
            tool_result = await tool_handler._handle_resource_analysis({})
            # logger.info(f"tool_result: {tool_result}")
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Resource leak analysis (full prompt)",
                )
                logger.info("Resource leak analysis prompt completed")
                return result
            else:
                 logger.warning("No result from tool for resource leak analysis")
                 return None                 
        except Exception as e:
            logger.error(f"Error in resource leak analysis: {e}")
            return None

    # Thêm vào class PromptHandler

    async def _handle_reset_analysis_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset analysis prompt - tự động gọi tool reset_analysic và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_analysis({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                result = types.GetPromptResult(
                    messages=messages,
                    description="Reset analysis result.",
                )
                logger.info("Reset analysis prompt completed")
                return result
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_analysic tool."),
                        )
                    ],
                    description="Reset analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset analysis prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting analysis: {e}"),
                    )
                ],
                description="Reset analysis error.",
            )
    
    async def _handle_reset_mem_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_mem_check prompt - tự động gọi tool reset_mem_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_mem_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset memory leak analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_mem_check tool."),
                        )
                    ],
                    description="Reset memory leak analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_mem_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting memory leak analysis: {e}"),
                    )
                ],
                description="Reset memory leak analysis error.",
            )

    async def _handle_reset_resource_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_resource_check prompt - tự động gọi tool reset_resource_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_resource_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset resource leak analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_resource_check tool."),
                        )
                    ],
                    description="Reset resource leak analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_resource_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting resource leak analysis: {e}"),
                    )
                ],
                description="Reset resource leak analysis error.",
            )

    async def _handle_reset_race_check_prompt(self, arguments: Dict[str, str] = None) -> types.GetPromptResult:
        """
        Handle reset_race_check prompt - tự động gọi tool reset_race_check và trả về kết quả.
        """
        from lgedv.handlers.tool_handlers import ToolHandler
        tool_handler = ToolHandler()
        try:
            tool_result = await tool_handler._handle_reset_race_check({})
            if tool_result and hasattr(tool_result[0], 'text'):
                tool_text = tool_result[0].text
                messages = [
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=tool_text),
                    )
                ]
                return types.GetPromptResult(
                    messages=messages,
                    description="Reset race analysis result.",
                )
            else:
                return types.GetPromptResult(
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text="No result from reset_race_check tool."),
                        )
                    ],
                    description="Reset race analysis result (no output).",
                )
        except Exception as e:
            logger.error(f"Error in reset_race_check prompt: {e}")
            return types.GetPromptResult(
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(type="text", text=f"Error resetting race analysis: {e}"),
                    )
                ],
                description="Reset race analysis error.",
            )
     
    def _format_resource_leak_summary(self, leaks: list) -> str:
        """Format a summary of resource leaks by type and severity"""
        summary = {}
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for leak in leaks:
            leak_type = leak.get('type', 'unknown')
            severity = leak.get('severity', 'medium')
            
            if leak_type not in summary:
                summary[leak_type] = 0
            
            summary[leak_type] += 1
            severity_counts[severity] += 1
        
        summary_text = f"**By Severity:** {severity_counts['critical']} Critical, {severity_counts['high']} High, {severity_counts['medium']} Medium, {severity_counts['low']} Low\n\n"
        summary_text += "**By Resource Type:**\n"
        
        for leak_type, count in summary.items():
            summary_text += f"- {leak_type.title()}: {count} leak(s)\n"
        
        return summary_text
    
    
    def _create_race_analysis_prompt_section(self, race_result: dict) -> str:
        """Create analysis prompt section with detailed race condition information (no grouping, no limit)"""
        prompt_section = "## 🎯 Priority Analysis Guidelines:\n\n"
        prompt_section += "1. Focus on shared state accessed by multiple threads.\n"
        prompt_section += "2. Ensure proper synchronization (mutexes, locks, atomics).\n"
        prompt_section += "3. Review thread creation and join/detach logic.\n"
        prompt_section += "4. Check for lock-free and concurrent data structure usage.\n"
        prompt_section += "5. Provide before/after code examples for fixes.\n\n"
        return prompt_section

    async def _handle_code_context(self) -> types.GetPromptResult:
        """Handle code context prompt (load and summarize all files in src_dir)"""
        import os
        prompt_lang = os.environ.get("prompt_lang", "en")
        if prompt_lang == "vi":
            prompt = (
                "Bạn là trợ lý ngữ cảnh mã nguồn. Nhiệm vụ của bạn là đọc và ghi nhớ toàn bộ nội dung, cấu trúc của tất cả các file mã nguồn (C++, Python, ...) trong thư mục dự án hiện tại.\n"
                "Nếu nội dung file chưa được tải, hãy gọi tool 'get_src_context' từ MCP server để lấy tất cả file mã nguồn trong thư mục SRC_DIR.\n"
                "Với mỗi file, hãy tóm tắt:\n"
                "- Tên file và đường dẫn tương đối\n"
                "- Tất cả class, struct, enum, function (C++, Python, ...)\n"
                "- Quan hệ kế thừa, sử dụng, thành phần\n"
                "- Biến toàn cục, hằng số, macro, cấu hình\n"
                "- Các chú thích hoặc tài liệu quan trọng\n"
                "Không thực hiện phân tích tĩnh hoặc kiểm tra rule ở bước này.\n"
                "Lưu ngữ cảnh này để dùng cho các truy vấn tiếp theo.\n\n"
                "**ĐỊNH DẠNG KẾT QUẢ:**\n"
                "Với mỗi file:\n"
                "### [Tên file]\n"
                "```[ngôn ngữ]\n[Tóm tắt cấu trúc, định nghĩa, điểm chính]\n```\n"
                "Lặp lại cho tất cả file.\n"
                "Xác nhận khi đã nạp đủ ngữ cảnh."
            )
        else:
            prompt = self.templates.get_context_prompt()
        messages = [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt),
            )
        ]
        result = types.GetPromptResult(
            messages=messages,
            description="A prompt for loading and summarizing code context for all C++ files.",
        )
        logger.info("Code context prompt completed")
        return result