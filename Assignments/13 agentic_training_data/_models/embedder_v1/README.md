---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:1102
- loss:MultipleNegativesRankingLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: 'Credential Stuffing: Adversaries may use credentials obtained
    from breach dumps of unrelated accounts to gain access to target accounts through
    credential overlap. Occasionally, large numbers of username and password pairs
    are dumped online when a website or service is compromised and the user account
    credentials accessed. The information may be useful to an adversary attempting
    to compromise accounts by taking advantage of the tendency for users to use the
    same passwords across personal and business accounts.…'
  sentences:
  - 'Defending login pages against brute-force attacks requires multiple layered controls,
    not a single silver bullet. Multi-Factor Authentication (MFA) is the single most
    effective control: even if a password is stolen or guessed, a second factor (TOTP
    app, hardware key, push notification) blocks the attacker. Rate limiting should
    restrict attempts to no more than 100 failed attempts per IP per hour, with progressive
    delays after 5 failures. Account lockout or step-up challenge (e.g., CAPTCHA or
    secondary email verification) must trigger after 10 to 20 failed attempts — lockout
    periods of 15-30 minutes are sufficient for most threats. Password spraying (low-volume
    guessing across many accounts) evades per-account lockout; detect it by monitoring
    for distributed failed login events across many accounts in a short window. Log
    aggregation and SIEM alerts on authentication anomalies are essential; a strong
    password policy alone does not prevent credential stuffing from leaked databases.'
  - '## Validating Free-form Unicode Text


    Free-form text, especially with Unicode characters, is perceived as difficult
    to validate due to a relatively large space of characters that need to be allowed.


    It''s also free-form text input that highlights the importance of proper context-aware
    output encoding and quite clearly demonstrates that input validation is **not**
    the primary safeguards against Cross-Site Scripting. If your users want to type
    apostrophe `''` or less-than sign `<` in their comment field, they might have
    perfectly legitimate reason for that and the application''s job is to properly
    handle it throughout the whole life cycle of the data.


    The primary means of input validation for free-form text input should be:


    - **Normalization:** Ensure canonical encoding is used across all the text and
    no invalid characters are present.

    - **Character category allowlisting:** Unicode allows listing categories such
    as "decimal digits" or "letters" which not only covers the Latin alphabet bu'
  - '## 8.2 Types of secrets to be detected


    Many types of secrets exist, and you should consider signatures for each to ensure
    accurate detection for all. Among the more common types are:


    - High availability secrets (Tokens that are difficult to rotate)

    - Application configuration files

    - Connection strings

    - API keys

    - Credentials

    - Passwords

    - 2FA keys

    - Private keys (e.g., SSH keys)

    - Session tokens

    - Platform-specific secret types (e.g., Amazon Web Services, Google Cloud)


    For more fun learning about secrets and practice rooting them out, check out the
    [Wrong Secrets](https://owasp.org/www-project-wrongsecrets/) project.'
- source_sentence: 'IP address: the numbers separated by periods whose role is to
    recognize every computer by use of the internet protocol to communicate over a
    network.'
  sentences:
  - 'Potential mitigations for CWE-601 - URL Redirection to Untrusted Site (''Open
    Redirect''):

    - [Implementation] Assume all input is malicious. Use an "accept known good" input
    validation strategy, i.e., use a list of acceptable inputs that strictly conform
    to specifications. Reject any input that does not strictly conform to specifications,
    or transform it into something that does. When…

    - [Architecture and Design] Use an intermediate disclaimer page that provides
    the user with a clear warning that they are leaving the current site. Implement
    a long timeout before the redirect occurs, or force the user to click on the link.
    Be careful to avoid XSS problems (CWE-79) when generating the…

    - [Architecture and Design] When the set of acceptable objects, such as filenames
    or URLs, is limited or known, create a mapping from a set of fixed input values
    (such as numeric IDs) to the actual filenames or URLs, and reject all other inputs.
    For example, ID 1 could map to "/login.asp" and ID 2 could…

    - ['
  - 'The product defines policy namespaces and makes authorization decisions based
    on the assumption that a URL is canonical. This can allow a non-canonical URL
    to bypass the authorization. If an application defines policy namespaces and makes
    authorization decisions based on the URL, but it does not require or convert to
    a canonical URL before making the authorization decision, then it opens the application
    to attack. For example, if the application only wants to allow access to http://www.example.com/mypage,
    then the attacker might be able to bypass this restriction using equivalent URLs
    such as: http://WWW.EXAMPLE.COM/mypage http://www.example.com/%6Dypage (alternate
    encoding) http://192.168.1.1/mypage (IP address) http://www.example.com/mypage/
    (trailing /) http://www.example.com:80/mypage Therefore it is important to specify
    access control policy that is based on the path information in some canonical
    form with all alternate encodings rejected (which can be accomplished by a default
    de'
  - The product allows address regions to overlap, which can result in the bypassing
    of intended memory protection. Isolated memory regions and access control (read/write)
    policies are used by hardware to protect privileged software. Software components
    are often allowed to change or remap memory region definitions in order to enable
    flexible and dynamically changeable memory management by system software. If a
    software component running at lower privilege can program a memory address region
    to overlap with other memory regions used by software running at higher privilege,
    privilege escalation may be available to attackers. The memory protection unit
    (MPU) logic can incorrectly handle such an address overlap and allow the lower-privilege
    software to read or write into the protected memory region, resulting in privilege
    escalation attack. An address overlap weakness can also be used to launch a denial
    of service attack on the higher-privilege software memory regions.
- source_sentence: 'Domains: Adversaries may acquire domains that can be used during
    targeting. Domain names are the human readable names used to represent one or
    more IP addresses. They can be purchased or, in some cases, acquired for free.
    Adversaries may use acquired domains for a variety of purposes, including for
    [Phishing](https://attack.mitre.org/techniques/T1566), [Drive-by Compromise](https://attack.mitre.org/techniques/T1189),
    and Command and Control.(Citation: CISA MSS Sep 2020) Adversaries may choose domains…'
  sentences:
  - The product contains a component that cannot be updated or patched in order to
    remove vulnerabilities or significant bugs. If the component is discovered to
    contain a vulnerability or critical bug, but the issue cannot be fixed using an
    update or patch, then the product's owner will not be able to protect against
    the issue. The only option might be replacement of the product, which could be
    too financially or operationally expensive for the product owner. As a result,
    the inability to patch or update can leave the product open to attacker exploitation
    or critical operation failures. This weakness can be especially difficult to manage
    when using ROM, firmware, or similar components that traditionally have had limited
    or no update capabilities. In industries such as healthcare, "legacy" devices
    can be operated for decades. As a US task force report [REF-1197] notes, "the
    inability to update or replace equipment has both large and small health care
    delivery organizations struggle with num
  - The product implements a conversion mechanism to map certain bus-transaction signals
    to security identifiers. However, if the conversion is incorrectly implemented,
    untrusted agents can gain unauthorized access to the asset. In a System-On-Chip
    (SoC), various integrated circuits and hardware engines generate transactions
    such as to access (reads/writes) assets or perform certain actions (e.g., reset,
    fetch, compute, etc.). Among various types of message information, a typical transaction
    is comprised of source identity (to identify the originator of the transaction)
    and a destination identity (to route the transaction to the respective entity).
    Sometimes the transactions are qualified with a security identifier. This security
    identifier helps the destination agent decide on the set of allowed actions (e.g.,
    access an asset for read and writes). A typical bus connects several leader and
    follower agents. Some follower agents implement bus protocols differently from
    leader agents. A proto
  - The product includes web functionality (such as a web widget) from another domain,
    which causes it to operate within the domain of the product, potentially granting
    total access and control of the product to the untrusted source. Including third
    party functionality in a web-based environment is risky, especially if the source
    of the functionality is untrusted. Even if the third party is a trusted source,
    the product may still be exposed to attacks and malicious behavior if that trusted
    source is compromised, or if the code is modified in transmission from the third
    party to the product. This weakness is common in "mashup" development on the web,
    which may include source functionality from other domains. For example, Javascript-based
    web widgets may be inserted by using '<SCRIPT SRC="http://other.domain.here">'
    tags, which causes the code to run in the domain of the product, not the remote
    site from which the widget was loaded. As a result, the included code has access
    to the local DOM,
- source_sentence: 'Google: redirection of 301, which will inform your browser the
    location header to go to www.'
  sentences:
  - '## Preventing XSS and Content Security Policy


    All user data controlled must be encoded when returned in the HTML page to prevent
    the execution of malicious data (e.g. XSS). For example `<script>` would be returned
    as `&lt;script&gt;`


    The type of encoding is specific to the context of the page where the user controlled
    data is inserted. For example, HTML entity encoding is appropriate for data placed
    into the HTML body. However, user data placed into a script would need JavaScript
    specific output encoding.


    Detailed information on XSS prevention here: [OWASP XSS Prevention Cheat Sheet](Cross_Site_Scripting_Prevention_Cheat_Sheet.md)'
  - 'Defense Evasion (TA0005) includes techniques adversaries use to avoid detection
    throughout their attack. Common techniques: T1036 Masquerading (naming malware
    to look like legitimate system processes — ''svch0st.exe'', ''explorer32.exe'');
    T1562 Impair Defenses (disabling antivirus, clearing event logs, stopping security
    services); T1027 Obfuscated Files or Information (base64 encoding, encryption
    of payloads to evade signature detection); T1055 Process Injection (injecting
    malicious code into legitimate processes like svchost.exe or explorer.exe). Detection
    approach: behavioural detection is more effective than signature-based detection
    against evasion techniques. Monitor for processes running from unusual paths,
    parent-child process anomalies, and event log clearing.'
  - '## Deny-list (Last Resort)


    **Deny-lists are bypass-prone. Prefer allow-lists.**


    **When unavoidable, block these minimum ranges:**


    | Service | Block IPs/Domains |

    |---------|-------------------|

    | **AWS IMDS** | `169.254.169.254`, `metadata.amazonaws.com` |

    | **GCP Metadata** | `metadata.google.internal`, `169.254.169.254` |

    | **Azure IMDS** | `169.254.169.254` |

    | **Localhost** | `127.0.0.0/8`, `0.0.0.0/8`, `::1/128` |

    | **RFC1918 Private** | `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` |

    | **Multicast** | `224.0.0.0/4`, `ff00::/8` |


    **Full production example:** [ComputerCraft SSRF deny-list](https://github.com/cc-tweaked/CC-Tweaked/blob/b9ed66983d714bcb5c6bf15b428e01a035106dbf/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L112-L157)


    **Sources:**


    - [IANA IPv4 Special Registry](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml)

    - [IANA IPv6 Special Registry](https://www.iana.org/assignmen'
- source_sentence: 'Brute Force: Adversaries may use brute force techniques to gain
    access to accounts when passwords are unknown or when password hashes are obtained.(Citation:
    TrendMicro Pawn Storm Dec 2020) Without knowledge of the password for an account
    or set of accounts, an adversary may systematically guess the password using a
    repetitive or iterative mechanism.(Citation: Dragos Crashoverride 2018) Brute
    forcing passwords can take place via interaction with a service that will check
    the validity of those credentials or…'
  sentences:
  - Originally, called Ethereal, Wireshark is a tool that comes with T-shark, a command
    line version. This network protocol can run on Windows, Linux, and OS X. It essentially
    enables you to capture and browse interactively, the composition of network frames.
    The purpose of the manufacturer was to create a commercial-quality analyzer for
    UNIX and give Wireshark the missing features that are missing from the sniffers
    that are generally closed-source. The tool is easy to use and has the ability
    to reconstruct TCP/IP streams.
  - '## Possible CSRF Vulnerabilities in Login Forms


    Most developers tend to ignore CSRF vulnerabilities on login forms as they assume
    that CSRF would not be applicable on login forms because user is not authenticated
    at that stage, however this assumption is not always true. CSRF vulnerabilities
    can still occur on login forms where the user is not authenticated, but the impact
    and risk is different.


    For example, if an attacker uses CSRF to assume an authenticated identity of a
    target victim on a shopping website using the attacker''s account, and the victim
    then enters their credit card information, an attacker may be able to purchase
    items using the victim''s stored card details. For more information about login
    CSRF and other risks, see section 3 of [this](https://seclab.stanford.edu/websec/csrf/csrf.pdf)
    paper.


    Login CSRF can be mitigated by creating pre-sessions (sessions before a user is
    authenticated) and including tokens in login form. You can use any of the techniques
    mentioned ab'
  - 'The product uses weak credentials (such as a default key or hard-coded password)
    that can be calculated, derived, reused, or guessed by an attacker. By design,
    authentication protocols try to ensure that attackers must perform brute force
    attacks if they do not know the credentials such as a key or password. However,
    when these credentials are easily predictable or even fixed (as with default or
    hard-coded passwords and keys), then the attacker can defeat the mechanism without
    relying on brute force. Credentials may be weak for different reasons, such as:
    Hard-coded (i.e., static and unchangeable by the administrator) Default (i.e.,
    the same static value across different deployments/installations, but able to
    be changed by the administrator) Predictable (i.e., generated in a way that produces
    unique credentials across deployments/installations, but can still be guessed
    with reasonable efficiency) Previously Compromised (i.e., "leaked" credentials
    that were published as part of a data b'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'BertModel'})
  (1): Pooling({'embedding_dimension': 384, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
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
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Brute Force: Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.(Citation: TrendMicro Pawn Storm Dec 2020) Without knowledge of the password for an account or set of accounts, an adversary may systematically guess the password using a repetitive or iterative mechanism.(Citation: Dragos Crashoverride 2018) Brute forcing passwords can take place via interaction with a service that will check the validity of those credentials or…',
    'The product uses weak credentials (such as a default key or hard-coded password) that can be calculated, derived, reused, or guessed by an attacker. By design, authentication protocols try to ensure that attackers must perform brute force attacks if they do not know the credentials such as a key or password. However, when these credentials are easily predictable or even fixed (as with default or hard-coded passwords and keys), then the attacker can defeat the mechanism without relying on brute force. Credentials may be weak for different reasons, such as: Hard-coded (i.e., static and unchangeable by the administrator) Default (i.e., the same static value across different deployments/installations, but able to be changed by the administrator) Predictable (i.e., generated in a way that produces unique credentials across deployments/installations, but can still be guessed with reasonable efficiency) Previously Compromised (i.e., "leaked" credentials that were published as part of a data b',
    'Originally, called Ethereal, Wireshark is a tool that comes with T-shark, a command line version. This network protocol can run on Windows, Linux, and OS X. It essentially enables you to capture and browse interactively, the composition of network frames. The purpose of the manufacturer was to create a commercial-quality analyzer for UNIX and give Wireshark the missing features that are missing from the sniffers that are generally closed-source. The tool is easy to use and has the ability to reconstruct TCP/IP streams.',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.4636, 0.1769],
#         [0.4636, 1.0000, 0.1320],
#         [0.1769, 0.1320, 1.0000]])
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

* Size: 1,102 training samples
* Columns: <code>sentence_0</code> and <code>sentence_1</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                          | sentence_1                                                                           |
  |:--------|:------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------|
  | type    | string                                                                              | string                                                                               |
  | details | <ul><li>min: 15 tokens</li><li>mean: 97.43 tokens</li><li>max: 154 tokens</li></ul> | <ul><li>min: 28 tokens</li><li>mean: 174.19 tokens</li><li>max: 256 tokens</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
  |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>Credentials: Adversaries may gather credentials that can be used during targeting. Account credentials gathered by adversaries may be those directly associated with the target victim organization or attempt to take advantage of the tendency for users to use the same passwords across personal and business accounts. Adversaries may gather credentials from potential victims in various ways, such as direct elicitation via [Phishing for Information](https://attack.mitre.org/techniques/T1598). Adversaries may…</code> | <code>## Sensitive information in HTTP requests<br><br>RESTful web services should be careful to prevent leaking credentials. Passwords, security tokens, and API keys should not appear in the URL, as this can be captured in web server logs, which makes them intrinsically valuable.<br><br>- In `POST`/`PUT` requests sensitive data should be transferred in the request body or request headers.<br>- In `GET` requests sensitive data should be transferred in an HTTP Header.<br><br>**OK:**<br><br>`https://example.com/resourceCollection/[ID]/action`<br><br>`https://twitter.com/vanderaj/lists`<br><br>**NOT OK:**<br><br>`https://example.com/controller/123/action?apiKey=a53f435643de32` because the apiKey is in the URL.</code>                                                                                                                                                                                                                                                                                                                                                                                                           |
  | <code>Software: Adversaries may gather information about the victim's host software that can be used during targeting. Information about installed software may include a variety of details such as types and versions on specific hosts, as well as the presence of additional components that might be indicative of added defensive protections (ex: antivirus, SIEMs, etc.). Adversaries may gather this information in various ways, such as direct collection actions via [Active…</code>                                           | <code>Potential mitigations for CWE-494 - Download of Code Without Integrity Check:<br>- [Implementation] Perform proper forward and reverse DNS lookups to detect DNS spoofing.<br>- [Architecture and Design, Operation] Encrypt the code with a reliable encryption scheme before transmitting. This will only be a partial solution, since it will not detect DNS spoofing and it will not prevent your code from being modified on the hosting site.<br>- [Architecture and Design] Use a vetted library or framework that does not allow this weakness to occur or provides constructs that make this weakness easier to avoid [REF-1482]. Speficially, it may be helpful to use tools or frameworks to perform integrity checking on the transmitted code. When providing…<br>- [Architecture and Design, Operation] Run your code using the lowest privileges that are required to accomplish the necessary tasks [REF-76]. If possible, create isolated accounts with limited privileges that are only used for a single task. That way, a succes</code>                                                                                             |
  | <code>Proxy: Adversaries may use a connection proxy to direct network traffic between systems or act as an intermediary for network communications to a command and control server to avoid direct connections to their infrastructure. Many tools exist that enable traffic redirection through proxies or port redirection, including [HTRAN](https://attack.mitre.org/software/S0040), ZXProxy, and ZXPortMap. (Citation: Trend Micro APT Attack Tools) Adversaries use these types of proxies to manage command and control…</code>    | <code>## Controlling Network Access to Sensitive Ports<br><br>It is highly recommended to configure authentication and authorization on the cluster and cluster nodes. Since Kubernetes clusters usually listen on a range of well-defined and distinctive ports, it is easier for attackers to identify the clusters and attack them.<br><br>An overview of the default ports used in Kubernetes is provided below. Make sure that your network blocks access to ports, and you should seriously consider limiting access to the Kubernetes API server to trusted networks.<br><br>**Control plane node(s):**<br><br>\| Protocol \| Port Range \| Purpose                 \|<br><br>\| -------- \| ---------- \| ----------------------- \|<br><br>\| TCP      \| 6443       \| Kubernetes API Server   \|<br><br>\| TCP      \| 2379-2380  \| etcd server client API  \|<br><br>\| TCP      \| 10250      \| Kubelet API             \|<br><br>\| TCP      \| 10259      \| kube-scheduler          \|<br><br>\| TCP      \| 10257      \| kube-controller-manager \|<br><br>\| TCP      \| 10255      \| Read-Only Kubelet API   \|<br><br>**Worker</code> |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `num_train_epochs`: 1
- `per_device_eval_batch_size`: 32
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 32
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
- `per_device_eval_batch_size`: 32
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
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Time
- **Training**: 10.6 seconds

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

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
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