# Changelog

## [0.2.1](https://github.com/griquelme/tidyms2/compare/v0.2.0...v0.2.1) (2025-08-31)


### Bug Fixes

* access pydantic model_fields using the model class ([6fd9ede](https://github.com/griquelme/tidyms2/commit/6fd9ede2f69bfdfa8310971b49bec1f23ca1db4a))
* add matrix operators to pipelines ([6b3eb1a](https://github.com/griquelme/tidyms2/commit/6b3eb1a487793dfb766a0bc72d853102efbe51bb))

## [0.2.0](https://github.com/griquelme/tidyms2/compare/v0.1.0...v0.2.0) (2025-08-30)


### Features

* add simulation utility to create list of samples ([01c7662](https://github.com/griquelme/tidyms2/commit/01c7662b34adaca869c743e75fae2a214199a19b))


### Bug Fixes

* ensure that submatrix has same status as parent matrix ([6cdf0e0](https://github.com/griquelme/tidyms2/commit/6cdf0e0665f8cd312a7b550b3bdcab2968e00b4c))
* expose matrix status as a property ([6df9263](https://github.com/griquelme/tidyms2/commit/6df9263478645afb0e5cf4544920f64c2e7ad978))
* fix type annotation ([8f3e160](https://github.com/griquelme/tidyms2/commit/8f3e1602595bffa55e39d121069cab7a3d41ff6d))

## 0.1.0 (2025-05-10)


### Features

* add `FeatureGroup.name` field ([a51ae0b](https://github.com/griquelme/tidyms2/commit/a51ae0b78c94c8298e211d9bf956a16a55e9eb0f))
* add `spawn_context` parameter to row and column matrix transformers ([0b9d89d](https://github.com/griquelme/tidyms2/commit/0b9d89d7106e284e1c43b6e1171f983f25559bd6))
* add `storage_path` parameter for assay data ([5c41bac](https://github.com/griquelme/tidyms2/commit/5c41bac364bb705738d7f575cb9e444d8da38e73))
* add algorithms package ([d100eb8](https://github.com/griquelme/tidyms2/commit/d100eb8f5b481c5b7b06f4520c62ed8c0c7ae0a1))
* Add annotated Numpy types IntArray and FloatArray ([f9e38d5](https://github.com/griquelme/tidyms2/commit/f9e38d5b4820fcd294ff2d123206396999e92662))
* add annotation package ([9aaa55f](https://github.com/griquelme/tidyms2/commit/9aaa55fac464ed8ee3e5ba2f5fbb3fff6228eda2))
* add assay subpackage ([6bab44f](https://github.com/griquelme/tidyms2/commit/6bab44f83d47fac194cbeae188d43a0afc5466bc))
* add Assay.create_matrix method ([3f93f4b](https://github.com/griquelme/tidyms2/commit/3f93f4be5fe7772badc2642ddf05b8fa9a24ecb5))
* add core.registry module ([bf9bbf5](https://github.com/griquelme/tidyms2/commit/bf9bbf564ed93ed84e3c26d710176d12d07c4a80))
* add data matrix metrics ([f35c0ae](https://github.com/griquelme/tidyms2/commit/f35c0ae346218413aca91077b86647f0c9f1c1de))
* add features and samples properties to data matrix ([27e919f](https://github.com/griquelme/tidyms2/commit/27e919f68ba7b228bbfb04dbd6e6cfeec6fc8e3d))
* add get_operator and list_operator_ids methods to Pipeline class ([94ba06f](https://github.com/griquelme/tidyms2/commit/94ba06fc1e424f3497b5c99303c951d50f1ad6f2))
* add lc-ms data matrix simulation ([1e0863f](https://github.com/griquelme/tidyms2/commit/1e0863fce4663e7f08b65878e630c6526a24cf59))
* add lc-ms sample builder utils ([01ba303](https://github.com/griquelme/tidyms2/commit/01ba303d99a8ca934cf174b8a4bf037087e9e325))
* add lcms.operators subpackage ([5d75fca](https://github.com/griquelme/tidyms2/commit/5d75fca0b6ebdb81d410e1e81c59337824468296))
* add lod and loq metrics ([c4af20b](https://github.com/griquelme/tidyms2/commit/c4af20b89382ebfa88ff9f482f8b321e412511fa))
* add missing imputation functionality ([5ca66aa](https://github.com/griquelme/tidyms2/commit/5ca66aa830e658ceda8faadc1554c80a5ac62a74))
* add MZTrace and Peak LC-MS models ([7fafdd6](https://github.com/griquelme/tidyms2/commit/7fafdd633499a46f5346b4dfe742adc47d8904de))
* add option to remove empty ROIs after sample processing ([fd4ca5b](https://github.com/griquelme/tidyms2/commit/fd4ca5bbf22e6cf62777bf9948f4d65c2ae56a84))
* add pipeline serialization/deserialization ([136a2dd](https://github.com/griquelme/tidyms2/commit/136a2dd1a54d256d97abbd48db5bbd88463c3dcc))
* add progenesis matrix reader ([373bb37](https://github.com/griquelme/tidyms2/commit/373bb37b267ee14618c2b54379749c415ce13810))
* add query and io APIs to data matrix ([ebb3e17](https://github.com/griquelme/tidyms2/commit/ebb3e174a91254ea806e8e619834ea626691aaff))
* Add SampleType core enumeration ([1ce951a](https://github.com/griquelme/tidyms2/commit/1ce951a8e6b3d48db763d7a3c8d508faba5a0604))
* add SQLite assay storage support for storing feature groups ([0a12f95](https://github.com/griquelme/tidyms2/commit/0a12f95c138a6d4fa83993754abe5fc40f97bb7d))
* add storage subpackage ([e808095](https://github.com/griquelme/tidyms2/commit/e8080954f0a95aba222278237975936525866ec9))
* add support for e2e data processing ([358a7da](https://github.com/griquelme/tidyms2/commit/358a7daaabbfe213948d38866bf42cb14f6920fd))
* Add utils subpackage ([38721fc](https://github.com/griquelme/tidyms2/commit/38721fc5a1a61590052b287e4d1af9a908f7ea78))
* **chem:** add `FormulaGeneratorConfiguration.update_bounds` method ([8278d47](https://github.com/griquelme/tidyms2/commit/8278d47151ca20700c193e9f2e2f82f9e6060038))
* **chem:** add chem subpackage ([b504d81](https://github.com/griquelme/tidyms2/commit/b504d816db7c72ef63d7b2ffdc88b8c3698aef45))
* **core:** add `get_roi_type` and `get_feature_type` methods to `AssayStorage` ([ed9b61b](https://github.com/griquelme/tidyms2/commit/ed9b61bed55bb83b16199db15c69183200436ce4))
* **core:** add `GroupAnnotation` to core models ([4fddf8d](https://github.com/griquelme/tidyms2/commit/4fddf8d17ec4da2b11ce331af2ec4078a6b4e038))
* **core:** add `MissingImputer` operator ([221ba26](https://github.com/griquelme/tidyms2/commit/221ba262de6f867d17b9c2cf83d9111669530601))
* **core:** add `MSSpectrum.get_nbytes` method ([6e77dc8](https://github.com/griquelme/tidyms2/commit/6e77dc8e9a3e479e0da7d9ca0b21fa27caa12aab))
* **core:** add `Pipeline.copy` method ([fc06693](https://github.com/griquelme/tidyms2/commit/fc066933c05d76ca350bf7de66261ce0e9b68011))
* **core:** add Assay class ([8e9cb4f](https://github.com/griquelme/tidyms2/commit/8e9cb4fde79b9c26408cad7f664517fc98f30493))
* **core:** Add core subpackage ([aaa7932](https://github.com/griquelme/tidyms2/commit/aaa79328d2ca546ccf2e59ffcd56a5e7ae6ba4c1))
* **core:** add core.utils.transformation.aggregate function ([50ceca9](https://github.com/griquelme/tidyms2/commit/50ceca9182eda2bca5ea81f1b9d8a04a453d0d55))
* **core:** add DataMatrix ([0c65fe8](https://github.com/griquelme/tidyms2/commit/0c65fe83d468580a13ceec528a52cf7f5bf48411))
* **core:** add FeatureTable class ([275b1ca](https://github.com/griquelme/tidyms2/commit/275b1ca15b9e435f662bbc95ce03e17b0d2e7e17))
* **core:** add metrics methods enums ([c72d118](https://github.com/griquelme/tidyms2/commit/c72d1185d54ed607d8c5201afd8d7017520fa4e7))
* **core:** add unprocessed sample exception ([eb61876](https://github.com/griquelme/tidyms2/commit/eb618762a6a63dcd0ca946f74137b7d56dd5c74b))
* **io:** add method to temporarily override MSData config ([641d58a](https://github.com/griquelme/tidyms2/commit/641d58a576151185e607e84b1c8ed5c0482922c9))
* **io:** add mzML reader ([dbd085d](https://github.com/griquelme/tidyms2/commit/dbd085d354cd11ce28cbef0c7fbc5dff91f83d2b))
* **io:** add utilities to download example dataset from GitHub ([2cc105a](https://github.com/griquelme/tidyms2/commit/2cc105aeb09f3ceb8afb8fb1ebc1263af952e478))
* **lcms:** add LC-MS assay utilities ([102f113](https://github.com/griquelme/tidyms2/commit/102f113be7612007fa934bd72018e4b744a98c28))
* **lcms:** add LC-MS sample operators ([b23d440](https://github.com/griquelme/tidyms2/commit/b23d440075426eac941f97906b93d3904c40a107))
* **lcms:** add LCMSFeatureMatcher ([6e8dec0](https://github.com/griquelme/tidyms2/commit/6e8dec06bcbd9d8e2d1e78a4dd914b7c669fa5de))
* **lcms:** add LCTraceSmoother ([6e18ffb](https://github.com/griquelme/tidyms2/commit/6e18ffb9ed084dd3e9259b4ba12695e838fbf143))
* **lcms:** add utilities to simulate lcms data ([73b1ae6](https://github.com/griquelme/tidyms2/commit/73b1ae6383e74cbb6e87d344784bc33a0b7b652c))
* pass SampleStorage configuration to assay constructor ([f429ba9](https://github.com/griquelme/tidyms2/commit/f429ba9a0d8ddd186516815e96f89226c27d1685))
* represent feature descriptors with pydantic computed fields ([752eb35](https://github.com/griquelme/tidyms2/commit/752eb35567d98a82a0390e14948e075207539091))
* **storage:** add `SQLiteAssayStorage` ([6c1901d](https://github.com/griquelme/tidyms2/commit/6c1901d9205092513d7af4760368345796a9dcfa))
* **utils:** add find_closest function ([4ecfaec](https://github.com/griquelme/tidyms2/commit/4ecfaec8b1acfef81e0add6f2721e27f4c56f370))


### Bug Fixes

* accept str values and enumeration in create_lcms_assay ([716347f](https://github.com/griquelme/tidyms2/commit/716347fe122b7d8f55d5a91f5ca3a9c8ee0542ee))
* add missing `get_process_status` and `set_process_status` methods to `OnMemoryAssayStorage` ([43483aa](https://github.com/griquelme/tidyms2/commit/43483aa272208babc793d5b3633108fe9dc6b1d3))
* **algorithms:** fill nan values in mz traces in make_roi function ([6ad9046](https://github.com/griquelme/tidyms2/commit/6ad9046aa298f76aa5df5048023ca2093104228a))
* **algorithms:** fix mz seed estimation for cases when the initial array contain a single element in make_roi ([0f12920](https://github.com/griquelme/tidyms2/commit/0f12920e2d41687f94263aa102d9ccbd85e99b09))
* **annotation:** implement get_expected_status_in and get_expected_status_out for IsotopologueAnnotator ([5786610](https://github.com/griquelme/tidyms2/commit/5786610798738b211c26095cd5cb781a76ebc356))
* baseline estimation return values lower or equal than signal ([5ce8e72](https://github.com/griquelme/tidyms2/commit/5ce8e72e4a6e7839daadf3c79f9ef6838db6df7d))
* **chem:** make `FormulaGeneratorConfiguration.max_M` a required parameter ([c04428d](https://github.com/griquelme/tidyms2/commit/c04428d9fcfaef499e05a4a25b0e459a38997705))
* **chem:** remove elements with a single isotope in envelope validator ([00958ca](https://github.com/griquelme/tidyms2/commit/00958ca3c057996990e4dac0557e41bd85034bab))
* compute formula envelope using a single envelope returns 1.0 ([3cf20ee](https://github.com/griquelme/tidyms2/commit/3cf20ee8d686b5d8eb2d6c173cc0c5950efebecd))
* **core:** Define Sample model before Roi model ([4491500](https://github.com/griquelme/tidyms2/commit/4491500512f248d59315d71abccf1d40db261499))
* fix border cases for nominal mass and mass defect bounds estimation ([239fc3e](https://github.com/griquelme/tidyms2/commit/239fc3e6850d226ccccef0af0c733da34d03979e))
* fix error when computing merge candidates during feature matching ([7131c14](https://github.com/griquelme/tidyms2/commit/7131c14e5c03cac83c4dbce3993ad68f10fda6df))
* fix ROI extrapolation in make_roi ([bc80b38](https://github.com/griquelme/tidyms2/commit/bc80b38c7abf85247f1a8649002d1c9c15c930d8))
* **lcms:** allow peak end equal to lc trace length in peak validator ([380fc20](https://github.com/griquelme/tidyms2/commit/380fc20366083ffbe39c1911ccf8fc3d1d879e29))
* **lcms:** peak descriptors return python floats ([74bbca8](https://github.com/griquelme/tidyms2/commit/74bbca8161bba93c12dbe14b76d229f7abed2490))
* **lcms:** remove MZTrace.smooth and MZTrace.fill_nan methods ([d7bc35f](https://github.com/griquelme/tidyms2/commit/d7bc35fc5118c5024520d7c7e1b898d20d19a754))
* manage empty envelope on validation ([aca6c2b](https://github.com/griquelme/tidyms2/commit/aca6c2be5a085a2143de0dcc5f192ba61480d534))
* move MZTrace to core.models to prevent circular imports ([f4e7b91](https://github.com/griquelme/tidyms2/commit/f4e7b91aee6731a057f150e030530f51dba7a79c))
* remove method list_samples from SampleStorage protocol ([f80c352](https://github.com/griquelme/tidyms2/commit/f80c352151203e14864c7c45a928dee9620dcaf0))
* set SeparationMode values to lowercase ([2fd0ffa](https://github.com/griquelme/tidyms2/commit/2fd0ffac97177ded024df14dd6476cfa8706f649))
* solve consesus annotations conflicts on two separate passes ([7caf310](https://github.com/griquelme/tidyms2/commit/7caf310430053ac27cfcbe11ddcb62075a653973))
* update feature group after annotation patching ([3eb8b36](https://github.com/griquelme/tidyms2/commit/3eb8b363dd52b215c34f324b4e8c396447f56704))
* use double underscore to name separate pipeline id from operator name in create_lc_assay ([63ae8d7](https://github.com/griquelme/tidyms2/commit/63ae8d752cd042d54ef3b44401a96b69d00ec9cf))
* use q=0 on MassQuery ([4c41a12](https://github.com/griquelme/tidyms2/commit/4c41a128883adffcbe44729aa474fe1be6b528a9))


### Documentation

* add algorithm docs ([47210d1](https://github.com/griquelme/tidyms2/commit/47210d116c6a3e7ffa6203bc69ceda8df6e6a4f7))
* add architecture overview docs ([f995165](https://github.com/griquelme/tidyms2/commit/f9951659c50751a143ce9328959e3d18342362ba))
* add badge to README ([8ebd950](https://github.com/griquelme/tidyms2/commit/8ebd9500861f936f7894d1bd63a3aacccb8f555d))
* add feature correspondence algorithm docs ([4d02832](https://github.com/griquelme/tidyms2/commit/4d02832fe07172c6835f6eef26b22ce3896f7e81))
* add link to developer guides in Roi docstring ([5c88789](https://github.com/griquelme/tidyms2/commit/5c88789ded4496f9b12faf9324987999000b6784))
* add mz trace extraction algorithm docs ([738330b](https://github.com/griquelme/tidyms2/commit/738330bb74ded708e9c50592fa0bd88ea9f483c2))
* add mzML docs ([0240824](https://github.com/griquelme/tidyms2/commit/0240824aa3286bf75f5790ba31c36afb64f228da))
* add peak extraction algorithm docs ([f2e555e](https://github.com/griquelme/tidyms2/commit/f2e555edccb6582295c3ca83d3e558527c72bbac))
* add simulation docs ([4883302](https://github.com/griquelme/tidyms2/commit/4883302936f5a5fecd963bd3e32a8d14b59c096d))
* add warning message to README ([13e204c](https://github.com/griquelme/tidyms2/commit/13e204cb8259a60bd7499210cae40a9b22b4a73f))
* fix raises directive in docstrings ([0bac1c6](https://github.com/griquelme/tidyms2/commit/0bac1c6485ae12666a040ebfb8237831b6555837))
* improve docs ([534003c](https://github.com/griquelme/tidyms2/commit/534003c66d2872b59c6b4242b4ee773a0460cb3d))
* minor fixes ([6b7c4a0](https://github.com/griquelme/tidyms2/commit/6b7c4a00c6dfca73e700b5b5ecdbb25c929714d6))
* Set up docs ([a47477d](https://github.com/griquelme/tidyms2/commit/a47477d2615135f098647c178d08801b9b3cc102))
* update architecture overview guide ([a103783](https://github.com/griquelme/tidyms2/commit/a103783cdd75dd5e73996cea36d525187e92c644))
