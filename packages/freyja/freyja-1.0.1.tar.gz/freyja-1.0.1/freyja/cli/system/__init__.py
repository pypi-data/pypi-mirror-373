from .completion import Completion
from .tune_theme import TuneTheme

class SystemClassBuilder:
  @staticmethod
  def build(completion:bool=True, theme_tuner:bool=False) -> type:
    system_class_dict:dict = {}

    if completion: system_class_dict['Completion'] = Completion
    if theme_tuner: system_class_dict['TuneTheme'] =  TuneTheme
    return type('System', (object,), system_class_dict)

# Create default System class for direct import
System = SystemClassBuilder.build(completion=True, theme_tuner=True)

__all__ = ['SystemClassBuilder', 'System', 'Completion', 'TuneTheme']
