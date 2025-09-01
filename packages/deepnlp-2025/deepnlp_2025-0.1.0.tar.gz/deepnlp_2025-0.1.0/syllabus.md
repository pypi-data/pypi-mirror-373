# 딥러닝자연어처리 (131307379A)

## 개요

최근 몇 년간 자연어 처리(NLP) 연구는 거대한 전환을 겪었다. 대규모 언어 모델(LLM)은 텍스트를 생성하고 이해하는 능력을 극적으로 향상시키며 번역, 질의응답, 요약 등 다양한 응용 분야의 판도를 바꾸어 놓았다. 2024~2025년에는 GPT-4o와 Gemini 1.5 Pro처럼 텍스트·이미지·음성까지 처리하는 멀티모달 모델이 등장하여 LLM의 활용 범위를 크게 확장했다. 특히 **Transformer를 넘어서는 새로운 아키텍처**의 등장이 주목된다. 예를 들어 **Mamba**와 같은 상태공간 모델(SSM)은 선형 O(n) 복잡도로 최대 100만 토큰까지 처리할 수 있으며 Transformer보다 5배 빠른 추론 속도를 제공한다.

이 강의는 이러한 최신 발전을 반영하여 **실습 중심의 심층 학습과 NLP 기법**을 배운다. 학생들은 초반에 PyTorch와 Hugging Face 도구 사용법을 익히고, 이후 Transformer 기반 모델 및 **최신 SSM 아키텍처**의 미세조정(fine-tuning), 프롬프트 엔지니어링(prompt engineering), 검색 증강 생성(RAG), 인간 피드백 강화 학습(RLHF), 에이전트 프레임워크 구현 등을 직접 경험한다. 아울러 **최신 파라미터 효율적 미세조정 기법**(WaveFT, DoRA, VB-LoRA)과 **고급 RAG 아키텍처**(HippoRAG, GraphRAG)를 다루며, 마지막으로 팀 프로젝트를 통해 배운 내용을 통합하여 실제 문제를 해결하는 모델을 완성한다.

본 과목은 학부 3학년 수준으로 설계되었으며 선수과목으로 _언어모형과 자연어처리 (131107967A)_ 이수를 전제로 한다. 팀 프로젝트를 통해 **한국어 코퍼스**를 활용한 실제 문제 해결에 도전하며, 최종 프로젝트 단계에서는 **산학 협력**을 고려하여 실제 산업 데이터셋을 다루고 업계 전문가로부터 피드백을 받을 기회를 제공한다.

### 교육 목표

- 현대 NLP에서 대규모 언어 모델의 역할과 한계를 이해하고 관련 도구(PyTorch, Hugging Face 등)를 활용한다.

- Transformer와 더불어 **State Space Model**(예: Mamba, RWKV) 등 최신 아키텍처의 원리와 장단점을 이해한다.

- 사전학습 모델을 fine-tuning하거나 **WaveFT, DoRA, VB-LoRA** 같은 최신 **매개변수 효율적 미세조정** 방법을 적용할 수 있다.

- **프롬프트 엔지니어링 기법**과 **DSPy 프레임워크**를 활용하여 프롬프트를 체계적으로 최적화하는 방법을 익힌다.

- 평가 지표의 발전(G-Eval, LiveCodeBench 등)과 인간 평가의 중요성을 이해하고, **DPO(Direct Preference Optimization)** 등 RLHF의 최신 대안을 학습한다.

- **HippoRAG, GraphRAG** 등 고급 RAG(Build Retrieval-Augmented Generation) 아키텍처와 하이브리드 검색 전략을 설계하고 구현한다.

- **EU AI Act** 등 AI 규제 프레임워크를 이해하고, 책임감 있는 AI 시스템 구현 방법론을 습득한다.

- 최신 연구 동향을 추적하여 멀티모달 LLM, 소형 언어 모델(SLM), 상태공간 모델(SSM), 혼합 전문가(MoE) 등 **최신 기술의 장단점**을 토의한다.

- **한국어 말뭉치**를 활용한 실습을 통해 한국어 NLP의 특성과 과제를 이해하고 적용 능력을 기른다.

- 팀 프로젝트를 통해 협업 및 실전 문제 해결 역량을 강화하며, 산업 현장과 연계한 프로젝트 경험을 쌓는다.

## 강의 계획

| 주차 | 주요 주제 및 키워드                                                                                                                 | 핵심 실습/과제                                                                           |
| :--: | :---------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
|  1   | Generative AI 소개, LLM의 발전, 최신 모델 (GPT-4o, Gemini 1.5 Pro, Claude 3 Opus)<br/>**Transformer의 한계와 새로운 아키텍처 소개** | PyTorch/Conda 환경 설정<br/>Hugging Face 파이프라인을 활용한 질의응답 데모               |
|  2   | PyTorch 기초, Hugging Face Transformers 사용법<br/>**Mamba 및 RWKV 아키텍처 소개**                                                  | 사전학습 모델(BERT) 로드 및 **한국어 데이터셋으로** 간단한 분류 실습<br/>Mamba 모델 데모 |
|  3   | 사전학습 모델 미세조정: fine-tuning vs. full-training<br/>**최신 State Space Model 실습**                                           | 프로그래밍 과제 1: Transformer와 SSM **성능 비교 실험 (한국어 분류 태스크)**             |
|  4   | **과학적 프롬프트 엔지니어링** – 다양한 기법, DSPy 프레임워크, 자동 프롬프트 최적화                                                 | DSPy를 활용한 프롬프트 자동 최적화 실습                                                  |
|  5   | **최신 평가 체계** – G-Eval, LiveCodeBench, MMLU-Pro 등 도메인별 벤치마크                                                           | LLM 기반 자동 평가 시스템 구축 실습                                                      |
|  6   | Seq2Seq 응용 및 **멀티모달 통합** – SmolVLM2, Qwen 2.5 Omni, 음성-텍스트 모델                                                       | 멀티모달 애플리케이션 개발 과제 2                                                        |
|  7   | 대규모 모델과 Few-shot 학습<br/>**초장문맥 처리 기술** (100만+ 토큰)                                                                | 장문맥 처리 전략 비교 실습                                                               |
|  8   | **차세대 PEFT** – WaveFT, DoRA, VB-LoRA, QLoRA 등 최신 기법                                                                         | 다양한 PEFT 기법 성능 비교 실험                                                          |
|  9   | **고급 RAG 시스템** – HippoRAG, GraphRAG, 하이브리드 검색 전략                                                                      | 과제 3: GraphRAG 기반 **한국어 엔터프라이즈 검색 시스템** 구축                           |
|  10  | **정렬 기법의 혁신** – DPO, Constitutional AI, Process Reward Models                                                                | DPO와 기존 RLHF 기법 비교 실습                                                           |
|  11  | **프로덕션 에이전트 시스템** – CrewAI, Mirascope, 타입-세이프티 개발                                                                | 멀티에이전트 오케스트레이션 구현                                                         |
|  12  | **AI 규제와 책임 있는 AI** – EU AI Act, 차등 프라이버시, 연합 학습                                                                  | 규제 준수 AI 시스템 설계 과제                                                            |
|  13  | **최신 연구 동향** – 소형 언어모델(Gemma 3, Mistral NeMo), 향상된 추론(Long CoT, PAL)                                               | 학생별 최신 논문 발표 및 종합 토론                                                       |
|  14  | 최종 프로젝트 개발 및 MLOps                                                                                                         | 팀별 프로토타입 구현 및 피드백 세션 **(산업 멘토 참여)**                                 |
|  15  | 프로젝트 최종 발표 및 종합 평가                                                                                                     | 팀별 발표, 강의 내용 총정리 및 미래 전망 토론                                            |

## 주차별 교육 내용

### 1주차 – 차세대 NLP 아키텍처의 이해

#### _핵심 주제_

- **Transformer를 넘어서:** 최근 연구에서 Transformer의 $O(n^2)$ 복잡도 한계를 극복하는 새로운 아키텍처들이 등장했다. 예를 들어 **Mamba**는 선택적 상태공간 모델(SSM)을 활용하여 **선형 시간**에 최대 100만 토큰의 시퀀스를 처리하며, **RWKV**는 하루 500만 개 이상의 메시지를 기존 대비 10~100배 저렴한 비용으로 실시간 처리할 수 있다.

- **하이브리드 아키텍처:** Jamba(총 52B 파라미터)는 Transformer와 Mamba를 혼합 전문가(MoE)로 결합하여 효율성과 성능을 모두 잡았다. 이와 함께 **선형 접근**을 활용한 Transformer 변형들(GLA, Sparse-K Attention 등)도 주목받고 있다.

- **오픈소스 모델의 약진:** Llama 3(405B), Mixtral 8×7B, Qwen2-72B 등 다수의 오픈소스 LLM이 GPT-4에 근접한 성능을 달성하며 산업 적용이 가속화되고 있다.

#### _실습/활동_

- **환경 설정:** Conda 가상환경 구성, PyTorch 및 Hugging Face Transformers 설치, **Mamba 라이브러리** 설치
- **데모:** 동일한 질의응답 태스크에 대해 Transformer 기반 모델과 Mamba 모델의 **추론 속도**를 비교 실험

### 2주차 – 도구 학습: PyTorch와 최신 프레임워크

- **프레임워크 기초:** PyTorch 텐서 연산 및 자동미분 기초, 최신 **FlashAttention-3** 활용법 (H100 GPU에서 1.5~2× 속도 향상)
- **생태계 도구:** Hugging Face Transformers 실습 및 **DSPy**, **Haystack**, **CrewAI** 등 특화된 NLP 프레임워크 소개
- **실습:** BERT와 Mamba 모델을 각각 로드하여 **동일한 한국어 텍스트 분류 작업**에서 성능과 효율성을 비교

### 3주차 – 효율적 미세조정의 최신 기법

- **차세대 PEFT 방법론:** 최신 매개변수 효율적 파인튜닝 기법들의 개념과 구현

  - **WaveFT:** 파라미터 업데이트를 주파수(웨이블릿) 영역에서 희소화하여 효율 향상
  - **DoRA:** 가중치 분해(Decomposition)를 통한 적응적 미세조정
  - **VB-LoRA:** 다중 사용자/태스크 환경을 위한 **벡터 뱅크** 기반 LoRA 확장
  - **QR-Adaptor:** 양자화 비트폭과 LoRA 랭크를 동시에 최적화하는 어댑터 기법

- **양자화의 진화:** 4-bit 양자화 포맷 **NF4 (NormalFloat4)**가 QLoRA의 표준으로 자리매김하여, 7B 모델을 메모리 약 10GB에서 ~1.5GB로 축소 가능
- **과제 1:** 동일 **한국어 데이터셋**에서 LoRA, DoRA, WaveFT의 성능을 비교 실험하여 파인튜닝 효율 및 성능 유지율 분석

### 4주차 – 프롬프트 엔지니어링의 과학화

- **체계적 프롬프트 기법:** 다양한 프롬프트 기법 사례 학습 (예: 역할 부여, 체계적 질문 등)
- **핵심 기법 심화:** 성능 향상을 이끈 주요 프롬프트 기법들

  - _Self-Consistency:_ 수학 문제 풀이에서 다중 해 경로 탐색으로 GSM8K 벤치마크 **17%p** 향상
  - _Tree of Thoughts:_ 문제 해결 시 사고의 가지를 확장하여 Game of 24 성공률 **74%** 달성 (기존 9% 대비)
  - _DSPy 프레임워크:_ "프롬프트를 프로그래밍하듯" 자동으로 최적 프롬프트를 생성/조합하는 패러다임

- **자동 프롬프트 최적화:** APE(Automatic Prompt Engineering) 기법을 통해 GSM8K에서 **93%**의 정답률 달성 등 사례 소개
- **실습:** DSPy를 활용하여 주어진 문제에 대한 **프롬프트 자동 최적화 파이프라인**을 구축하고 결과를 기존 기법과 비교

### 5주차 – 차세대 평가 시스템

- **평가 패러다임의 변화:** 전통적 정답 일치 평가에서 벗어나 LLM을 활용한 메타 평가로 전환

  - _G-Eval:_ GPT-4 기반 LLM이 체인-of-Thought를 사용하여 다른 LLM의 응답 품질을 평가
  - _LiveCodeBench:_ 온라인 코드 콘테스트 방식을 차용한 **오염 방지**형 코드 평가
  - _MMLU-Pro:_ 선택지가 4→10개로 늘고 다단계 추론을 요구하는 멀티턴 지식 평가 세트

- **도메인별 벤치마크:** 금융 도메인의 FinBen (36개 금융 태스크 세트), 에이전트 위험성 평가 AgentHarm (110개 악성 에이전트 시나리오) 등 특화 벤치마크
- **실습:** G-Eval과 기존 자동 평가 지표(BLEU, ROUGE 등)를 동일 응답에 적용하여 결과를 비교 분석

### 6주차 – 멀티모달 NLP의 혁신

- **"Any-to-Any" 모델 등장:** 범용 입력/출력 처리 모델들의 발전

  - _SmolVLM2 (256M–2.2B):_ 소형 파라미터로 **비디오 이해**까지 수행하는 경량 비전언어 모델
  - _Qwen 2.5 Omni:_ 텍스트-이미지-음성 간 상호 변환 가능한 통합 멀티모달 아키텍처
  - _QVQ-72B (프리뷰):_ 최초의 오픈소스 거대 멀티모달 추론 모델 (텍스트→비전→쿼리 형태 변환)

- **음성 통합의 발전:** LLM에 실시간 음성 처리 접목

  - _Voxtral:_ Whisper를 능가하는 성능의 오픈소스 음성 인식 모델
  - _Orpheus:_ 제로샷으로 화자의 목소리를 복제·합성하는 TTS 모델

- **과제 2:** 이미지-텍스트-음성 입력이 **혼합된 질의**에 대응하는 멀티모달 QA 애플리케이션 개발 (예: 음성으로 질문하고 이미지와 텍스트로 답변 생성)

### 7주차 – 장문맥 처리와 효율적 추론

- **극한의 문맥 확장:** 초장문맥 지원 LLM의 등장

  - _Gemini 1.5 Pro:_ 최대 **100만 토큰**까지 처리 가능한 거대 멀티모달 모델 (연구 버전은 1000만 토큰 목표)
  - _Magic LTM-2-Mini:_ 경제적인 구조로 **1억 토큰** 문맥창을 구현 (동일 성능에서 Llama 대비 비용 1/1000 수준)

- **효율적 장문맥 메커니즘:** Flash Linear Attention, LongRoPE (긴 문맥 위치 인코딩) 등 초장문맥 구현 기법 분석
- **실습:** 장문맥 대화 시나리오에 대해 **RAG (Retrieval-Augmented Generation)** 기반 요약 시스템 구현 및 초장문맥 LLM과의 성능 비교

### 8주차 – 최신 PEFT 기법 심화

- **경량 미세조정으로 95% 성능 달성:** 전체 파인튜닝 대비 성능 저하 없이 <1% 파라미터만 변경하는 최신 방법들
- **주요 기법 비교:** 각 PEFT 방법의 실제 구현 난이도와 효과 비교

  - 메모리 사용량(저장 공간) 비교
  - 추론 속도 및 지연 시간 벤치마크
  - 하나의 프롬프트로 다중 태스크 적응 가능성 평가

- **실습:** 주어진 NLP 태스크에 대해 여러 PEFT 방법으로 미세조정 실험을 진행하고, **프로덕션 환경**에서의 활용을 고려한 PEFT 선택 가이드 작성

### 9주차 – 고급 RAG 아키텍처

- **차세대 RAG 시스템:** 대용량 지식 통합을 위한 신규 기법

  - _HippoRAG:_ 인간 기억(Hippocampus) 메커니즘을 차용하여 벡터 DB 저장 공간을 **25% 절감**하고 장기 기억력을 향상
  - _GraphRAG:_ 지식 그래프를 활용해 문맥 간 연관성을 모델링, 질의 응답 정밀도 **99%**까지 향상
  - 하이브리드 검색: 최신 밀집 임베딩(NV-Embed-v2)과 희소 기법(SPLADE), 그래프 탐색을 조합한 멀티팩터 검색

- **프로덕션 사례:** 일일 1000만 개 이상의 입력 토큰을 처리하면서도 **P95 응답 지연 <100ms**를 달성한 대규모 RAG 시스템 구조 분석
- **과제 3:** GraphRAG 기반 **한국어 엔터프라이즈 검색** 시스템을 구축하여 사내 지식베이스 질의응답에 적용

### 10주차 – 정렬 기법의 혁신

- **RLHF를 넘어서:** LLM 출력의 유용성과 안전성을 높이기 위한 새로운 접근법

  - _DPO (Direct Preference Optimization):_ 별도의 보상 모델을 사용하지 않고 사용자 선호 학습 (RLHF 대비 간소화)
  - _Constitutional AI:_ AI 스스로 75개 이상의 헌법 원칙에 따라 응답을 교정하여 유해 콘텐츠 생성 억제
  - _Process Supervision:_ 최종 답변이 아니라 **과정(Chain-of-Thought)**에 대해 세분화된 피드백을 주는 보상모델 기법
  - _RLAIF (RL from AI Feedback):_ 인간 대신 AI 평가자를 활용하여 인간 수준의 응답 품질을 모방

- **오픈소스 구현 동향:** TRL (Transformer Reinforcement Learning) 라이브러리, OpenRLHF 프로젝트 등 공개 구현체 소개 (기존 DeepSpeed-Chat 대비 3~4× 속도 개선)
- **실습:** 동일한 제어 지침에 대해 DPO로 미세조정한 모델과 RLHF로 미세조정한 모델의 응답을 비교 평가

### 11주차 – 프로덕션 에이전트 시스템

- **전문화된 에이전트 프레임워크:** 실제 서비스에 활용되는 에이전트 개발 도구 소개

  - _CrewAI:_ 역할 기반 멀티에이전트 협업 시나리오 구축 프레임워크 (예: 다수의 GPT 인스턴스에 역할을 분담시켜 팀처럼 작동)
  - _Mirascope:_ Pydantic 데이터 검증으로 프롬프트 입력/출력의 **타입 안정성**을 높인 에이전트 개발 도구
  - _Haystack:_ 문서 RAG 파이프라인에 특화된 오픈소스 프레임워크 (검색-독해 체인의 커스터마이징 용이)

- **저코드 통합 플랫폼:** Flowise AI, n8n, Langflow 등 프롬프트와 워크플로를 GUI로 설계할 수 있는 도구 활용
- **실습:** 멀티에이전트 프레임워크를 활용하여 **자동화 고객 상담 시스템** 구현 (예: FAQ 답변, 데이터베이스 조회, 이슈 티켓 발행 에이전트 연계)

### 12주차 – AI 규제와 책임 있는 AI

- **EU AI Act (2024년 8월 시행):** 세계 최초의 포괄적 AI 법규의 주요 내용과 개발자/서비스 제공자 영향 분석
- **프라이버시 강화 기술:** 생성형 AI 서비스에 필요한 개인정보 및 민감정보 보호 기법

  - 텍스트 임베딩에 **차등 프라이버시** 도입하여 사용자 데이터 노출 방지
  - 중앙 서버 없이 협업 학습하는 **연합 학습 (Federated Learning)** 활용
  - 모델 학습에 암호화된 데이터를 활용하는 **동형 암호화** 기술

- **산업별 규제 준수:** 의료 분야 HIPAA, 금융 분야 GDPR/바젤, 교육 분야 FERPA 등 **도메인별 규제**에 맞춘 NLP 솔루션 설계 사례
- **과제:** 주어진 시나리오에 대해 EU AI Act 기준 **적합한 LLM 서비스** 설계 및 법규 준수 체크리스트 작성

### 13주차 – 최신 연구 동향과 미래 전망

- **소형 언어 모델의 르네상스:** 경량 모델들의 약진과 최적화 기법

  - _Gemma 3 (1B~4B):_ 소비자 기기에서도 원활히 동작하도록 최적화된 초경량 LLM 시리즈
  - _Mistral NeMo 12B:_ NVIDIA NeMo 최적화를 통해 **128K 토큰** 문맥창을 구현한 12B 모델 (긴 대화/문서 처리 특화)
  - _MathΣtral 7B:_ Mistral 기반으로 수학 문제에 특화된 모델 (MATH 벤치마크 **74.59%** 기록, 기존 GPT-4 수준 접근)

- **추론 능력의 진화:** 복잡한 문제 해결을 위한 LLM의 새로운 시도들

  - _Long CoT:_ 매우 긴 Chain-of-Thought를 활용, 필요 시 **백트래킹**과 오류 수정까지 수행하는 추론 기법
  - _PAL (Program-Aided Language Modeling):_ 코드 실행 능력을 결합하여 수치 계산이나 논리 추론 정확도 향상
  - _ReAct:_ 추론 중 **외부 도구 활용**(예: 계산기, 웹검색)을 병행하여 보다 정확하고 사실적인 답변 생성

- **배포 및 최적화 프레임워크:** 경량화/최적화된 LLM 배포를 위한 도구 현황

  - _llama.cpp:_ CPU 상에서 LLM 실행을 가능케 한 경량화 C++ 구현
  - _MLC-LLM:_ 모바일/웹 브라우저에서 LLM 추론을 지원하는 WebGPU 기반 런타임
  - _PowerInfer-2:_ 대규모 모델 추론 시 전력 효율을 극대화한 분산 추론 프레임워크

- **학생 발표:** 조별로 선정한 최신 논문을 리뷰 및 발표하고, 해당 연구의 의의와 한계, 미래 연구 방향에 대해 토론

### 14주차 – 최종 프로젝트 개발 및 MLOps

- **NLP 모델 MLOps:** 실제 서비스에 적용하기 위한 NLP MLOps 개념과 도구

  - 모델 버전관리 및 A/B 테스트 기법
  - 사용자 피드백을 활용한 지속적 학습 파이프라인 구축
  - 실시간 모니터링과 성능 저하(드리프트) 감지 시스템

- **팀별 프로젝트 개발:** 각 팀별로 선정한 주제에 대한 **프로토타입 모델** 개발 진행 상황 점검
- **산업 멘토 리뷰:** 초청된 업계 멘토들과 프로젝트 진행 상황 리뷰 세션을 갖고 피드백을 수렴 (산업계 요구사항 반영 여부, 실용성 평가 등)

### 15주차 – 산업 응용 사례 분석 및 최종 발표

- **산업별 NLP 성공 사례:**

  - 의료: 임상 기록 자동화 NLP로 의사 문서작성 부담 **49% → 27%** 감소 (의료 도메인 특화 LLM 활용)
  - 금융: Morgan Stanley의 법률 분석 봇 COIN 도입으로 연간 **36만 시간**의 업무량 절감
  - 교육: 맞춤형 학습 및 다국어 지원 튜터 AI로 학습 효율 향상 (학생 참여도 30% 증가)

- **최종 발표:** 팀별 프로젝트 결과 발표 및 데모 시연 (모델 아키텍처, 시연 결과 및 한계 공유)
- **강좌 종합 토의:** 강의 내용 전체 요약 및 질의응답, 미래 전망 브레인스토밍 (학생 피드백 수렴 및 향후 학습 가이드)

## 참고자료

### 최신 아키텍처 및 모델

- Gu & Dao (2023). _Mamba: Linear-Time Sequence Modeling with Selective State Spaces._
- Peng et al. (2023). _RWKV: Reinventing RNNs for the Transformer Era._
- Lieber et al. (2024). _Jamba: A Hybrid Transformer-Mamba Language Model._

### 파라미터 효율적 학습

- Zhang et al. (2024). _WaveFT: Wavelet-based Parameter-Efficient Fine-Tuning._
- Liu et al. (2024). _DoRA: Weight-Decomposed Low-Rank Adaptation._
- Chen et al. (2024). _VB-LoRA: Vector Bank for Efficient Multi-Task Adaptation._

### 프롬프트 엔지니어링과 평가

- Khattab et al. (2023). _DSPy: Compiling Declarative Language Model Calls._
- Liu et al. (2023). _G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment._
- Jain et al. (2024). _LiveCodeBench: Holistic and Contamination Free Evaluation._

### RAG와 지식 통합

- Zhang et al. (2024). _HippoRAG: Neurobiologically Inspired Long-Term Memory._
- Edge et al. (2024). _GraphRAG: A Modular Graph-Based RAG Approach._
- Chen et al. (2024). _Hybrid Retrieval-Augmented Generation: Best Practices._

### 정렬과 책임 있는 AI

- Rafailov et al. (2023). _Direct Preference Optimization: Your Language Model is Secretly a Reward Model._
- Bai et al. (2022). _Constitutional AI: Harmlessness from AI Feedback._
- EU Commission (2024). _EU AI Act: Implementation Guidelines._

### 산업 응용 및 배포

- _Healthcare NLP Market Report 2024–2028_. Markets and Markets.
- _Financial Services AI Applications 2025_. McKinsey Global Institute.
- _State of AI in Education 2025_. Stanford HAI.

### 개발 도구 및 프레임워크

- **CrewAI Documentation:** [https://docs.crewai.com/](https://docs.crewai.com/)
- **DSPy Official Guide:** [https://dspy-docs.vercel.app/](https://dspy-docs.vercel.app/)
- **OpenRLHF Project:** [https://github.com/OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)
