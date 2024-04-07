# Autogenerated by nbdev

d = { 'settings': { 'branch': 'main',
                'doc_baseurl': '/https://github.com/alex4321/bitlinear',
                'doc_host': 'https://alex4321.github.io',
                'git_url': 'https://github.com/alex4321/https://github.com/alex4321/bitlinear',
                'lib_path': 'bitlinear'},
  'syms': { 'bitlinear.adapters': { 'bitlinear.adapters.LinearAdapter': ('adapters.html#linearadapter', 'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LinearAdapter.calculate_weight_update': ( 'adapters.html#linearadapter.calculate_weight_update',
                                                                                                  'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LinearAdapter.forward': ( 'adapters.html#linearadapter.forward',
                                                                                  'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LinearAdapter.reset': ( 'adapters.html#linearadapter.reset',
                                                                                'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LoRAAdapter': ('adapters.html#loraadapter', 'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LoRAAdapter.__init__': ( 'adapters.html#loraadapter.__init__',
                                                                                 'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LoRAAdapter.calculate_weight_update': ( 'adapters.html#loraadapter.calculate_weight_update',
                                                                                                'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LoRAAdapter.forward': ( 'adapters.html#loraadapter.forward',
                                                                                'bitlinear/adapters.py'),
                                    'bitlinear.adapters.LoRAAdapter.reset': ('adapters.html#loraadapter.reset', 'bitlinear/adapters.py'),
                                    'bitlinear.adapters.MergeableLayer': ('adapters.html#mergeablelayer', 'bitlinear/adapters.py'),
                                    'bitlinear.adapters.MergeableLayer.__init__': ( 'adapters.html#mergeablelayer.__init__',
                                                                                    'bitlinear/adapters.py'),
                                    'bitlinear.adapters.MergeableLayer.merge_adapter': ( 'adapters.html#mergeablelayer.merge_adapter',
                                                                                         'bitlinear/adapters.py')},
            'bitlinear.bitlinear': { 'bitlinear.bitlinear.BitLinear': ('bitlinear.html#bitlinear', 'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.__init__': ( 'bitlinear.html#bitlinear.__init__',
                                                                                 'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear._quantize_weight': ( 'bitlinear.html#bitlinear._quantize_weight',
                                                                                         'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear._update_parameter': ( 'bitlinear.html#bitlinear._update_parameter',
                                                                                          'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear._wrap_parameters': ( 'bitlinear.html#bitlinear._wrap_parameters',
                                                                                         'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.forward': ( 'bitlinear.html#bitlinear.forward',
                                                                                'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.get_dequantized_weights': ( 'bitlinear.html#bitlinear.get_dequantized_weights',
                                                                                                'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.get_stored_weights': ( 'bitlinear.html#bitlinear.get_stored_weights',
                                                                                           'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.merge_adapter': ( 'bitlinear.html#bitlinear.merge_adapter',
                                                                                      'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.BitLinear.update_weights': ( 'bitlinear.html#bitlinear.update_weights',
                                                                                       'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._generate_parameter_mappings': ( 'bitlinear.html#_generate_parameter_mappings',
                                                                                           'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._generate_parameter_mappings_tensor': ( 'bitlinear.html#_generate_parameter_mappings_tensor',
                                                                                                  'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._generate_reverse_mapping_tree': ( 'bitlinear.html#_generate_reverse_mapping_tree',
                                                                                             'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._get_parameter_count_per_n_bits': ( 'bitlinear.html#_get_parameter_count_per_n_bits',
                                                                                              'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._render_condition': ( 'bitlinear.html#_render_condition',
                                                                                'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._render_condition_lines': ( 'bitlinear.html#_render_condition_lines',
                                                                                      'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear._render_multicondition_function': ( 'bitlinear.html#_render_multicondition_function',
                                                                                              'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.build_quantization_group_getter': ( 'bitlinear.html#build_quantization_group_getter',
                                                                                              'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.dequantize_weights': ( 'bitlinear.html#dequantize_weights',
                                                                                 'bitlinear/bitlinear.py'),
                                     'bitlinear.bitlinear.quantize_weights': ('bitlinear.html#quantize_weights', 'bitlinear/bitlinear.py')},
            'bitlinear.models.mistral': { 'bitlinear.models.mistral.BitMistralAdaptersMixin': ( 'mistral.html#bitmistraladaptersmixin',
                                                                                                'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAdaptersMixin._get_bitlinear_layers': ( 'mistral.html#bitmistraladaptersmixin._get_bitlinear_layers',
                                                                                                                      'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAdaptersMixin.add_adapters': ( 'mistral.html#bitmistraladaptersmixin.add_adapters',
                                                                                                             'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAdaptersMixin.mergeable_layers': ( 'mistral.html#bitmistraladaptersmixin.mergeable_layers',
                                                                                                                 'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAdaptersMixin.remove_adapters': ( 'mistral.html#bitmistraladaptersmixin.remove_adapters',
                                                                                                                'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAttention': ( 'mistral.html#bitmistralattention',
                                                                                            'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAttention.__init__': ( 'mistral.html#bitmistralattention.__init__',
                                                                                                     'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAttentionBase': ( 'mistral.html#bitmistralattentionbase',
                                                                                                'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralAttentionBase.__init__': ( 'mistral.html#bitmistralattentionbase.__init__',
                                                                                                         'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralDecoderLayer': ( 'mistral.html#bitmistraldecoderlayer',
                                                                                               'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralDecoderLayer.__init__': ( 'mistral.html#bitmistraldecoderlayer.__init__',
                                                                                                        'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralFlashAttention2': ( 'mistral.html#bitmistralflashattention2',
                                                                                                  'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralFlashAttention2.__init__': ( 'mistral.html#bitmistralflashattention2.__init__',
                                                                                                           'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralForCausalLM': ( 'mistral.html#bitmistralforcausallm',
                                                                                              'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralForCausalLM.__init__': ( 'mistral.html#bitmistralforcausallm.__init__',
                                                                                                       'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralForSequenceClassification': ( 'mistral.html#bitmistralforsequenceclassification',
                                                                                                            'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralForSequenceClassification.__init__': ( 'mistral.html#bitmistralforsequenceclassification.__init__',
                                                                                                                     'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralMLP': ( 'mistral.html#bitmistralmlp',
                                                                                      'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralMLP.__init__': ( 'mistral.html#bitmistralmlp.__init__',
                                                                                               'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralModel': ( 'mistral.html#bitmistralmodel',
                                                                                        'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralModel.__init__': ( 'mistral.html#bitmistralmodel.__init__',
                                                                                                 'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralPreTrainedModel': ( 'mistral.html#bitmistralpretrainedmodel',
                                                                                                  'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralPreTrainedModel._init_weights': ( 'mistral.html#bitmistralpretrainedmodel._init_weights',
                                                                                                                'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralSdpaAttention': ( 'mistral.html#bitmistralsdpaattention',
                                                                                                'bitlinear/models/mistral.py'),
                                          'bitlinear.models.mistral.BitMistralSdpaAttention.__init__': ( 'mistral.html#bitmistralsdpaattention.__init__',
                                                                                                         'bitlinear/models/mistral.py')},
            'bitlinear.relora': { 'bitlinear.relora.ReLoRAOptimizer': ('relora.html#reloraoptimizer', 'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.__init__': ( 'relora.html#reloraoptimizer.__init__',
                                                                                 'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer._cleanup': ( 'relora.html#reloraoptimizer._cleanup',
                                                                                 'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer._initialize_optimizer': ( 'relora.html#reloraoptimizer._initialize_optimizer',
                                                                                              'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.load_state_dict': ( 'relora.html#reloraoptimizer.load_state_dict',
                                                                                        'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.param_groups': ( 'relora.html#reloraoptimizer.param_groups',
                                                                                     'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.state_dict': ( 'relora.html#reloraoptimizer.state_dict',
                                                                                   'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.step': ('relora.html#reloraoptimizer.step', 'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRAOptimizer.zero_grad': ( 'relora.html#reloraoptimizer.zero_grad',
                                                                                  'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRASchedulerLambda': ('relora.html#reloraschedulerlambda', 'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRASchedulerLambda.__call__': ( 'relora.html#reloraschedulerlambda.__call__',
                                                                                       'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRASchedulerLambda.__init__': ( 'relora.html#reloraschedulerlambda.__init__',
                                                                                       'bitlinear/relora.py'),
                                  'bitlinear.relora.ReLoRASchedulerLambda._wrap_lr_lambda': ( 'relora.html#reloraschedulerlambda._wrap_lr_lambda',
                                                                                              'bitlinear/relora.py'),
                                  'bitlinear.relora.is_pickleable': ('relora.html#is_pickleable', 'bitlinear/relora.py')}}}
