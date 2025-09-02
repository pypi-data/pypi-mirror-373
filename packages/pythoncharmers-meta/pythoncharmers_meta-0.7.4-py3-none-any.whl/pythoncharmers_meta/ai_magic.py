from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
import llm


@magics_class
class AIMagic(Magics):

    def __init__(self, shell, default_model_name='gpt-4o-mini'):
        # You must call the parent constructor
        super().__init__(shell)
        self.default_model = llm.get_model(default_model_name)
        
    @magic_arguments()
    @argument("-m", "--model", type=str, help="Model name to use")
    @argument("-t", "--temperature", type=float, help="Sampling temperature")
    @argument("prompt", nargs="*", help="Prompt text (for line magic)")
    @line_cell_magic
    def ai(self, line, cell=None):
        # Parse arguments
        args = parse_argstring(self.ai, line)
        options = vars(args)

        # Combine cell content and line prompt
        prompt = " ".join(args.prompt) + ("" if cell is None else "\n\n" + cell)

        if "model" in options:
            model = llm.get_model(options["model"])
        else:
            model = self.default_model
            
        # Prepare options to pass to llm
        completion_args = {
            k: v for k, v in options.items() if k not in {"prompt", "model"} and v is not None
        }

        # Call llm and return response
        response = model.prompt(prompt, **completion_args)
        print(response.text())
        
