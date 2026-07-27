---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:5998
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/ms-marco-MiniLM-L6-v2
pipeline_tag: text-ranking
library_name: sentence-transformers
---

# CrossEncoder based on cross-encoder/ms-marco-MiniLM-L6-v2

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/ms-marco-MiniLM-L6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2) <!-- at revision c5ee24cb16019beea0893ab7796b1df96625c6b8 -->
- **Maximum Sequence Length:** 512 tokens
- **Number of Output Labels:** 1 label
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

### Full Model Architecture

```
CrossEncoder(
  (0): Transformer({'transformer_task': 'sequence-classification', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'logits'}}, 'module_output_name': 'scores', 'architecture': 'BertForSequenceClassification'})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of inputs
pairs = [
    ["magnet: The magnet's movement in and out of the helix causes a deflection in the galvanometer needle.", "In §17 Faraday thrust a cylindrical bar magnet 'twelve inches long' into 'a helix of two hundred and twenty turns' wound on a hollow pasteboard cylinder. While the magnet was at rest inside the coil, the galvanometer showed no deflection whatsoever. The moment the magnet was pushed in, a transient deflection appeared; on withdrawing it, the deflection was in the opposite direction. Moving the magnet faster produced a stronger deflection. In §26 Faraday concluded: 'a conductor must cut across the magnetic curves of force to generate an electromotive force.' The position of the magnet was irrelevant; only the act of cutting was decisive."],
    ['electro-chemical decomposition: The experiment demonstrates that the electro-chemical decomposition does not occur as a result of mutual dependence between the poles.', '§563. Having thus given my theory of the mode in which electro-chemical decomposition is effected, I will refrain for the present from entering upon the numerous general considerations which it suggests, wishing first to submit it to the test of publication and discussion. _Royal Institution, June 1833._ SIXTH SERIES. S 12. _On the power of Metals and other Solids to induce the Combination of Gaseous Bodies._ Received November 30, 1833,--Read January 11, 1834.'],
    ['conductor: The conductor is essential for completing the communication between the zinc and copper plates of the electromotor and can take various forms such as a helix or wire.', '§465. Arrangements were then made in which no metallic communication with the decomposing matter was allowed, but both poles (if they might now be called by that name) formed of air only. A piece of turmeric paper _a_ fig. 50, and a piece of litmus paper _b_, were dipped in solution of sulphate of soda, put together so as to form one moist pointed conductor, and supported on wax between two needle points, one, _p_, connected by a wire with the conductor of the machine, and the other, _n_, with the discharging train. The interval in each case between the points was about half an inch; the positive point _p_ was opposite the litmus paper; the negative point _n_ opposite the turmeric. The machine was then worked for a time, upon which evidence of decomposition quickly appeared, for the point of the litmus _b_ became reddened from acid evolved there, and the point of the turmeric _a_ red from a similar and simultaneous evolution of alkali. §466. Upon turning the paper conductor round, so t'],
    ["conducting particles: Conducting particles in the shell-lac can diminish the effectiveness of the dielectric, affecting the apparatus's performance.", '§559. Air, however, and some gases are free from the latter objection, and may be used as poles in many cases (461, &c.); but, in consequence of the extremely low degree of conducting power belonging to them, they cannot be employed with the voltaic apparatus. This limits their use; for the voltaic apparatus is the only one as yet discovered which supplies sufficient quantity of electricity (371. 376.) to effect electro-chemical decomposition with facility. §560. When the poles are liable to the chemical action of the substances evolved, either simply in consequence of their natural relation to them, or of that relation aided by the influence of the current (518.), then they suffer corrosion, and the parts dissolved are subject to transference, in the same manner as the particles of the body originally under decomposition. An immense series of phenomena of this kind might be quoted in support of the view I have taken of the cause of electro-chemical decomposition, and the transfer and '],
    ['electric current: Electric current refers to the flow of electricity that can produce a deflecting force on a magnetic needle in a galvanometer.', '§620. Bodies which become wetted by fluids with which they do not combine chemically, or in which they do not dissolve, are simple and well-known instances of this kind of attraction. §621. All those cases of bodies which being insoluble in water and not combining with it are hygrometric, and condense its vapour around or upon their surface, are stronger instances of the same power, and approach a little nearer to the cases under investigation. If pulverized clay, protoxide or peroxide of iron, oxide of manganese, charcoal, or even metals, as spongy platina or precipitated silver, be put into an atmosphere containing vapour of water, they soon become moist by virtue of an attraction which is able to condense the vapour upon, although not to combine it with, the substances; and if, as is well known, these bodies so damped be put into a dry atmosphere, as, for instance, one confined over sulphuric acid, or if they be heated, then they yield up this water again almost entirely, it not bei'],
]
scores = model.predict(pairs)
print(scores)
# [ 6.6193  3.3282  3.2062  2.609  -3.4175]

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    "magnet: The magnet's movement in and out of the helix causes a deflection in the galvanometer needle.",
    [
        "In §17 Faraday thrust a cylindrical bar magnet 'twelve inches long' into 'a helix of two hundred and twenty turns' wound on a hollow pasteboard cylinder. While the magnet was at rest inside the coil, the galvanometer showed no deflection whatsoever. The moment the magnet was pushed in, a transient deflection appeared; on withdrawing it, the deflection was in the opposite direction. Moving the magnet faster produced a stronger deflection. In §26 Faraday concluded: 'a conductor must cut across the magnetic curves of force to generate an electromotive force.' The position of the magnet was irrelevant; only the act of cutting was decisive.",
        '§563. Having thus given my theory of the mode in which electro-chemical decomposition is effected, I will refrain for the present from entering upon the numerous general considerations which it suggests, wishing first to submit it to the test of publication and discussion. _Royal Institution, June 1833._ SIXTH SERIES. S 12. _On the power of Metals and other Solids to induce the Combination of Gaseous Bodies._ Received November 30, 1833,--Read January 11, 1834.',
        '§465. Arrangements were then made in which no metallic communication with the decomposing matter was allowed, but both poles (if they might now be called by that name) formed of air only. A piece of turmeric paper _a_ fig. 50, and a piece of litmus paper _b_, were dipped in solution of sulphate of soda, put together so as to form one moist pointed conductor, and supported on wax between two needle points, one, _p_, connected by a wire with the conductor of the machine, and the other, _n_, with the discharging train. The interval in each case between the points was about half an inch; the positive point _p_ was opposite the litmus paper; the negative point _n_ opposite the turmeric. The machine was then worked for a time, upon which evidence of decomposition quickly appeared, for the point of the litmus _b_ became reddened from acid evolved there, and the point of the turmeric _a_ red from a similar and simultaneous evolution of alkali. §466. Upon turning the paper conductor round, so t',
        '§559. Air, however, and some gases are free from the latter objection, and may be used as poles in many cases (461, &c.); but, in consequence of the extremely low degree of conducting power belonging to them, they cannot be employed with the voltaic apparatus. This limits their use; for the voltaic apparatus is the only one as yet discovered which supplies sufficient quantity of electricity (371. 376.) to effect electro-chemical decomposition with facility. §560. When the poles are liable to the chemical action of the substances evolved, either simply in consequence of their natural relation to them, or of that relation aided by the influence of the current (518.), then they suffer corrosion, and the parts dissolved are subject to transference, in the same manner as the particles of the body originally under decomposition. An immense series of phenomena of this kind might be quoted in support of the view I have taken of the cause of electro-chemical decomposition, and the transfer and ',
        '§620. Bodies which become wetted by fluids with which they do not combine chemically, or in which they do not dissolve, are simple and well-known instances of this kind of attraction. §621. All those cases of bodies which being insoluble in water and not combining with it are hygrometric, and condense its vapour around or upon their surface, are stronger instances of the same power, and approach a little nearer to the cases under investigation. If pulverized clay, protoxide or peroxide of iron, oxide of manganese, charcoal, or even metals, as spongy platina or precipitated silver, be put into an atmosphere containing vapour of water, they soon become moist by virtue of an attraction which is able to condense the vapour upon, although not to combine it with, the substances; and if, as is well known, these bodies so damped be put into a dry atmosphere, as, for instance, one confined over sulphuric acid, or if they be heated, then they yield up this water again almost entirely, it not bei',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 5,998 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                            | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                             | string                                                                                | float                                                          |
  | details | <ul><li>min: 17 tokens</li><li>mean: 29.85 tokens</li><li>max: 43 tokens</li></ul> | <ul><li>min: 101 tokens</li><li>mean: 221.86 tokens</li><li>max: 368 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.51</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                     | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | label            |
  |:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>magnet: The magnet's movement in and out of the helix causes a deflection in the galvanometer needle.</code>                                                                             | <code>In §17 Faraday thrust a cylindrical bar magnet 'twelve inches long' into 'a helix of two hundred and twenty turns' wound on a hollow pasteboard cylinder. While the magnet was at rest inside the coil, the galvanometer showed no deflection whatsoever. The moment the magnet was pushed in, a transient deflection appeared; on withdrawing it, the deflection was in the opposite direction. Moving the magnet faster produced a stronger deflection. In §26 Faraday concluded: 'a conductor must cut across the magnetic curves of force to generate an electromotive force.' The position of the magnet was irrelevant; only the act of cutting was decisive.</code>                                                                                                                                                                                                                                                                                                                                                                      | <code>1.0</code> |
  | <code>electro-chemical decomposition: The experiment demonstrates that the electro-chemical decomposition does not occur as a result of mutual dependence between the poles.</code>            | <code>§563. Having thus given my theory of the mode in which electro-chemical decomposition is effected, I will refrain for the present from entering upon the numerous general considerations which it suggests, wishing first to submit it to the test of publication and discussion. _Royal Institution, June 1833._ SIXTH SERIES. S 12. _On the power of Metals and other Solids to induce the Combination of Gaseous Bodies._ Received November 30, 1833,--Read January 11, 1834.</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | <code>1.0</code> |
  | <code>conductor: The conductor is essential for completing the communication between the zinc and copper plates of the electromotor and can take various forms such as a helix or wire.</code> | <code>§465. Arrangements were then made in which no metallic communication with the decomposing matter was allowed, but both poles (if they might now be called by that name) formed of air only. A piece of turmeric paper _a_ fig. 50, and a piece of litmus paper _b_, were dipped in solution of sulphate of soda, put together so as to form one moist pointed conductor, and supported on wax between two needle points, one, _p_, connected by a wire with the conductor of the machine, and the other, _n_, with the discharging train. The interval in each case between the points was about half an inch; the positive point _p_ was opposite the litmus paper; the negative point _n_ opposite the turmeric. The machine was then worked for a time, upon which evidence of decomposition quickly appeared, for the point of the litmus _b_ became reddened from acid evolved there, and the point of the turmeric _a_ red from a similar and simultaneous evolution of alkali. §466. Upon turning the paper conductor round, so t</code> | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 1
- `per_device_eval_batch_size`: 16

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 1
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: trackio
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Time
- **Training**: 43.8 seconds

### Framework Versions
- Python: 3.10.11
- Sentence Transformers: 5.4.1
- Transformers: 5.5.4
- PyTorch: 2.6.0+cu124
- Accelerate: 1.13.0
- Datasets: 4.8.4
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->