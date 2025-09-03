from typing import final
from cement import Controller, ex
import itertools;
from ..core.config import load_config, generate_autocomplete_script

class GenerateBase(Controller):
    class Meta:
        label = 'generate_base'


class Generate(Controller):
    config = load_config('config.yml')

    class Meta:
        label = 'generate'
        stacked_on = 'generate_base'
        stacked_type = 'nested'
        
    @ex(
        help="Make and integrate tab autocompletion script",
    )
    def tab_completion(self):
        config = self.config
        
        base_paths_list = [
            config['php']['paths'] if 'php' in config else [],
            config['node']['paths'] if 'node' in config else [],
            config['python']['paths'] if 'python' in config else [],
            config['php_next']['paths'] if 'php_next' in config else []
        ]
               
        final_list = list(itertools.chain.from_iterable(base_paths_list))
           
        generate_autocomplete_script(final_list)