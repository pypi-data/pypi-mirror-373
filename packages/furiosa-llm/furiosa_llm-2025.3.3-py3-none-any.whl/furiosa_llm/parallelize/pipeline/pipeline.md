# 중간 파이프라인 형식 명세

## 목적
본 문서는 중간 파이프라인 형식을 구체화하고 각 필드 별 자세한 설명을 위해 작성되었음.  


## 명세

### **타입**

### Pipeline

중간 파이프라인을 나타내는 형식

| Name       | Type                                   | Description                ****                                                                                                  | Key                    |
| ---------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| name       | string                                 | 파이프라인의 이름                                                                                                                |
| devices    | map<string, [Device](#Device)>         | 파이프라인 실행을 위해 필요한 장치 슬롯들에 대한 정보                                                                            | 각 장치 슬롯 아이디    |
| tensors    | map<string, [TensorInfo](#TensorInfo)> | 파이프라인 내 텐서들에 대한 정보                                                                                                 | 각 텐서의 이름         |
| supertasks | map<string, [SuperTask](#SuperTask)>   | 파이프라인 내 수퍼태스크들에 대한 정보                                                                                           | 각 수퍼태스크의 아이디 |
| metadata   | [Metadata](#Metadata)                  | Generator에게 전달되기 위한 목적의 정보로 병렬화 전 모델의 온전한 입출력 텐서와 현재 파이프라인의 입출력 텐서 간의 관계를 명시함 |

### Device
하나의 장치 슬롯에 대한 정보

TODO: NPU의 fusioned pe 및 multi-machine 환경까지 표현할 수 있는 형식 구상 필요

| Name | Type   | Description                |
| ---- | ------ | -------------------------- |
| kind | string | 장치의 종류(`cpu`, `npu`) |
| idx  | uint64 | 머신 내 장치의 인덱스      |

### TensorInfo

파이프라인 내 존재하는 텐서의 정보

파이프라인 내에는 다음과 같은 두 종류의 텐서가 존재할 수 있다.
- 상수 텐서: 입력에 관계 없이 일정한 값을 가지며 파이프라인 실행 전에 로드되어 정적으로 존재하는 텐서들로 모델 내 가중치 파라미터들이나 고정된 값을 가지는 버퍼 텐서들이 이에 해당한다.
- 변수 텐서: 입력에 따라 값이 달라질 수 있으며 실행 중 동적으로 생성되는 중간 결과 (activation)나 입/출력 텐서가 이에 해당한다. 

| Name  | Type                      | Description                          | Required                         |
| ----- | ------------------------- | ------------------------------------ | -------------------------------- |
| shape | uint64[]                  | 해당 텐서의 모양                     | O                                |
| dtype | [DType](#DType)           | 해당 텐서의 데이터 타입              | O                                |
| value | [ParamValue](#ParamValue) | 상수 텐서의 값을 로드할 수 있는 방법 | 상수 텐서인 경우에만 존재해야 함 |

### DType

`f64`, `f32`, `f16`, `bf16`, `f8`, `bool`, `i64`, `i32`, `i16`, `i8` 중 하나의 값을 가지는 string

### ParamValue
| Name          | Type                                | Description                                                            |
| ------------- | ----------------------------------- | ---------------------------------------------------------------------- |
| path          | string                              | 상수 텐서가 저장되어있는 파라미터 저장 파일의 경로                     |
| format        | [ParamfileFormat](#ParamfileFormat) | 파라미터 저장 파일의 형식                                              |
| name          | string                              | 파라미터 저장 파일 내 해당 텐서를 식별하기 위한 이름                   |
| name_in_graph | string                              | 해당 텐서의 FX graph / dfg 내 이름                                     |
| placements    | [Placements](#Placements)           | 상수 텐서가 파라미터 저장 파일의 특정 텐서의 어떤 일부인지에 대한 정보 |

### Placements

Type: `List[Tuple[uint64, uint64]]`


특정 텐서의 일부를 지정할 수 있는 형식으로 i번째 원소는 해당 tensor의 i번째 차원에서 취할 범위이며 이 범위는 시작 인덱스와 끝 인덱스로 표현된다. 여기서 시작 인덱스는 범위에 포함되며 끝 인덱스는 범위에 포함되지 않는다. 

예를 들어 placements가 `[(1,3), (0, 2)]`인 경우 Pytorch 문법 상으로 가리키는 텐서의 일부는 `original_tensor[1:3, 0:2]`가 된다.

즉, 해당하는 일부는 첫번째 범위부터 마지막 범위를 모두 원본 텐서의 해당하는 차원에 적용한 결과물이며, Placements의 길이는 원본 텐서의 차원 수와 같아야 한다.


### ParamfileFormat

다음 값들 중 하나를 가진다.

* ["safetensors"](https://github.com/huggingface/safetensors)
* ["torch.save"](https://pytorch.org/docs/stable/generated/torch.save.html)
* ["torch.export"](https://pytorch.org/docs/stable/export.html)

### SuperTask

| Name       | Type                            | Description                                                                                                                                              | Required                                                                                                        |
| ---------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| kind       | [SuperTaskKind](#SuperTaskKind) | SuperTask의 종류                                                                                                                                         | O                                                                                                               |
| inputs     | string[]                        | SuperTask의 입력 텐서들의 이름으로 Pipeline.tensors의 key로서 존재해야 하며 이 SuperTask는 명시된 tensor들을 명시된 순서로 입력으로 받아 실행되어야 한다 | O                                                                                                               |
| outputs    | string[]                        | SuperTask의 출력 텐서들의 이름으로 Pipeline.tensors의 key로서 존재해야 하며 이 SuperTask는 실행 결과로 명시된 tensor들을 명시된 순서로 만들어낸다        | O                                                                                                               |
| device     | string                          | SuperTask가 실행되는 장치 슬롯의 id로 해당 id는 Pipeline.devices의 key로서 존재해야 함                                                                   | 계산 수퍼태스크 혹은 통신 수퍼태스크인 경우 반드시 존재해야 하며 입력, 출력 수퍼태스크의 경우에는 존재하면 안됨 |
| data       | string                          | 직렬화된 dfg 혹은 FX graph                                                                                                                               | 계산 수퍼태스크인 경우에만 존재해야 함                                                                          |
| group      | string                          | 통신 수퍼태스크가 속해 있는 통신 그룹으로 서로 대응하는 통신 수퍼태스크들끼리는 같은 통신 그룹을 가져야 함                                               | 통신 수퍼태스크인 경우에만 존재해야 함                                                                          |
| device_idx | uint64                          | 통신 그룹 내 통신 수퍼태스크가 실행되는 장치 슬롯의 인덱스                                                                                               | 통신 수퍼태스크인 경우에만 존재해야 함                                                                          |
| metadata   | map<string, uint64/string>      | 통신 수퍼태스크 실행에 필요한 추가적인 데이터들. 자세한 내용은 [각 통신 수퍼태스크별 필요 메타데이터](#각-통신 수퍼태스크별-필요-메타데이터) 참조        | 통신 수퍼태스크인 경우에만 존재해야 함                                                                          |

#### SuperTaskKind
다음 값들 중 하나를 가져야 한다.

- 계산 수퍼태스크 (`dfg`, `FX`)
    - 통신 연산이 존재하지 않고 하나의 디바이스에서 모두 실행될 수 있는 계산 연산만으로 이루어진 수퍼태스크
    - dfg 혹은 FX graph 형태일 수 있다.
- 통신 수퍼태스크 (`send`, `recv`, `reduce`, `all_gather`, `all_reduce`, `reduce_scatter`, `all_to_all`, `broadcast`)
    - 이름에 대응하는 통신 연산에 해당하는 수퍼태스크
    - 참고: DTensor 기반 구현으로는 `all_reduce`, `all_gather`, `reduce_scatter`만 생성됨
- 입력, 출력 수퍼태스크 (`input`, `output`)
    - 입력 수퍼태스크는 입력은 없으며 파이프라인의 입력 텐서들을 출력으로 내보내는 수퍼태스크이다
    - 출력 수퍼태스크는 출력은 없으며 파이프라인의  출력 텐서들을 입력으로 받는 수퍼태스크이다

#### 각 통신 수퍼태스크별 필요 메타데이터

각 통신 수퍼태스크는 `SuperTaskKind`에 따라 `SuperTask.metadata` 내에 정확히 아래와 같은 key 및 value들을 가져야 함 

- `send`
    - 없음
- `recv`
    - 없음
- `reduce`
    - `reduce_op`: string
        - reduce할 함수의 종류로 (`sum`, `avg` , `max` , `min`) 중 하나의 값을 가져야 함 (일단은 `sum`만 고려)
    - `dst`: string 
        - 최종 결과물이 생성될 장치 슬롯의 id
- `all_gather`
    - `dim`: uint64
        - concat 연산이 수행될 차원
- `all_reduce`
    - `reduce_op`: string
        - reduce할 함수의 종류로 (`sum`, `avg` , `max` , `min`) 중 하나의 값을 가져야 함 (일단은 `sum`만 고려)
- `reduce_scatter`
    - `reduce_op`: string
        - reduce할 함수의 종류로 (`sum`, `avg` , `max` , `min`) 중 하나의 값을 가져야 함 (일단은 `sum`만 고려)
    - `dim`: uint64
        - reduce된 결과물이 각 디바이스에 나눠질 차원
- `all_to_all`
    - `src_dim`: uint64
        - 각 장치 슬롯의 입력 텐서들이 나뉘어질 차원, 각 장치 슬롯의 입력 텐서는 `src_dim` 으로 나뉘어져 균일한 장치 개수 만큼의 텐서가 생성되고 i번째 조각은 통신 그룹 내 i번째 장치 슬롯에게 보내진다.
    - `dst_dim`: uint64
        - 다른 장치로부터 받은 텐서들을 병합(concat)할 차원
- `broadcast`
    - `src`: string 
        - 데이터를 보내는 장치 슬롯의 id (`string`)

### Metadata

Metadata는 Generator가 내외부에서 전달 및 생성되는 텐서들을 어떤 식으로 가공하여 Pipeline에 입력으로 넣어야 할지에 대한 정보를 포함한다. 해당 정보는 Pipeline Runner에 의해서는 사용되지 않는다.


| Name          | Type                                          | Description                                                                                         |
| ------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| tensors       | [MetadataTensors](#MetadataTensors)           | 병렬화 전 원본 모델 (FX graph 기준)의 입/출력 텐서들에 대한 정보                                    |
| tensor_slices | [MetadataTensorSlices](#MetadataTensorSlices) | 중간 파이프라인의 입/출력 텐서들에 대한 정보로 유래한 원본 입/출력 텐서들과의 관계에 대한 정보 포함 |


### MetadataTensors

| Name    | Type                                           | Description                                             | key                   |
| ------- | ---------------------------------------------- | ------------------------------------------------------- | --------------------- |
| inputs  | map<string, [MetadataTensor](#MetadataTensor)> | 병렬화 전 원본 모델 (FX graph 기준)의 입력 텐서 별 정보 | 해당 입력 텐서의 이름 |
| outputs | map<string, [MetadataTensor](#MetadataTensor)> | 병렬화 전 원본 모델 (FX graph 기준)의 출력 텐서 별 정보 | 해당 출력 텐서의 이름 |

#### 입/출력 텐서의 이름이 지어지는 방식

* 해당 입/출력 텐서가 원본 모델의 온전한 하나의 인자/반환 결과에 정확히 대응되는 경우 원본 모델에서 사용되는 이름을 그대로 따른다.
    * (e.g., input_ids, logits)  
* 해당 입/출력 텐서가 원본 모델의 온전한 하나의 인자/반환 결과의 일부인 경우 원본 모델에서 사용되는 이름에 아래 규칙을 따라 접미사가 붙은 이름을 가진다.
    * (nested) list 혹은 tuple인 경우 `{원본_이름}_{첫번째 인덱스}_{두번째 인덱스}_ ...._{마지막 인덱스}` 의 이름을 가진다.
        * e.g, transformers 모델의 kv cache 중 4번째 transformer block의 v cache의 이름은 `past_key_values_3_1`임
    * 다른 경우에 대해서는 아직 필요성이 없어 정의되지 않았다. 필요한 경우 추가해야 함.


### MetadataTensor

병렬화 전 원본 모델 (FX graph 기준)의 입력 혹은 출력 텐서에 대한 정보

| Name       | Type            | Description                                                                          |
| ---------- | --------------- | ------------------------------------------------------------------------------------ |
| shape      | uint64[]        | 해당 텐서의 모양                                                                     |
| dtype      | [DType](#DType) | 해당 텐서의 데이터 타입                                                              |
| idx        | uint64          | 원본 모델을 트레이싱하여 FX graph를 생성하였을 때 입력 텐서들 내 해당 텐서의 인덱스  |

#### `idx` 관련 추가 설명

원본 모델의 트레이싱 결과로 생성된 FX graph는 여러 개의 입력을 받을 수 있지만, 각 입력은 항상 Pytorch Tensor 이어야 한다. 그렇기 때문에 원본 Pytorch 모델이 각 원소가 Pytorch Tensor인 집합체 타입 (collection type)인 경우 각 원소가 별개의 입력으로 쪼개지게 된다. 예를 들어 원본 모델이 `[8, 2]` (num_hidden_layers=8) 모양의 튜플 형태 kv cache를 인자들 중 하나로 받는 경우 이 인자는 트레이싱 후 각각이 일반 텐서인 16개의 입력으로 쪼개지게 된다. `idx` 필드는 원본 모델 기준이 아니라 FX graph를 기준으로 입력들의 리스트 중 해당 텐서의 인덱스를 의미한다.

TODO: 장기적으로는 이렇게 FX tracing을 통해 흩어진 인자를 하나로 합치는 방법에 대해서도 중간 파이프라인 형식에 명시되어야 한다.

### MetadataTensorSlices

중간 파이프라인의 입/출력 텐서들에 대한 정보로 유래한 원본 입/출력 텐서들과의 관계에 대한 정보 포함

| Name    | Type                                                     | Description                               | Key                   |
| ------- | -------------------------------------------------------- | ----------------------------------------- | --------------------- |
| inputs  | map<string, [MetadataTensorSlice](#MetadataTensorSlice)> | 중간 파이프라인의 입력 텐서들에 대한 정보 | 해당 입력 텐서의 이름 |
| outputs | map<string, [MetadataTensorSlice](#MetadataTensorSlice)> | 중간 파이프라인의 출력 텐서들에 대한 정보 | 해당 출력 텐서의 이름 |

### MetadataTensorSlice

| Name       | Type                      | Description                                                           |
| ---------- | ------------------------- | --------------------------------------------------------------------- |
| placements | [Placements](#Placements) | 해당 입/출력 텐서가 유래한 원본 입/출력 텐서의 어떤 일부에 해당하는지 |
| origin     | string                    | 유래한 원본 입/출력 텐서의 이름                                       |
| dtype      | [DType](#DType)           | 해당 입/출력 텐서의 데이터타입                                        |
| device     | string                    | 해당 입/출력 텐서가 존재하는 장치 슬롯의 id                           |
