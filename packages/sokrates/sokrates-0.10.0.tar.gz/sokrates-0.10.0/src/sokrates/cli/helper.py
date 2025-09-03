from sokrates import FileHelper
from sokrates import OutputPrinter
from sokrates import Colors
from sokrates.config import Config

class Helper:
  
    @staticmethod
    def construct_context_from_arguments(context_text: str = None, context_directories: str = None, context_files: str = None):
        context = []
        if context_text:
            context.append(context_text)
            OutputPrinter.print_info("Appending context text to prompt:", context_text , Colors.BRIGHT_MAGENTA)
        if context_directories:
            directories = [s.strip() for s in context_directories.split(",")]
            context.extend(FileHelper.read_multiple_files_from_directories(directories))
            OutputPrinter.print_info("Appending context directories to prompt:", context_directories , Colors.BRIGHT_MAGENTA)
        if context_files:
            files = [s.strip() for s in context_files.split(",")]
            context.extend(FileHelper.read_multiple_files(files))
            OutputPrinter.print_info("Appending context files to prompt:", context_files , Colors.BRIGHT_MAGENTA)
        return context

    @staticmethod
    def print_configuration_section(config: Config, args=None):
        api_endpoint_config_source = f"Configuration File: {config.config_path}"
        api_endpoint = config.api_endpoint
        
        api_endpoint_config_source = "CLI Parameter: --api-endpoint"
        
        if args and args.api_endpoint:
            api_endpoint = args.api_endpoint
            api_endpoint_config_source = "CLI Parameter: --api-endpoint"

        OutputPrinter.print_section("Configuration")
        OutputPrinter.print_info("Sokrates home", config.home_path)
        OutputPrinter.print_info("Configuration source", api_endpoint_config_source)
        OutputPrinter.print_info("LLM API Endpoint", api_endpoint)
