# paGating Architecture Data Flow

```mermaid
graph TD
    A[Input Tokens: x] --> B[GPT-2 Transformer Blocks]
    B --> C[MLP Layer]
    C --> D[Linear: fc_in]
    D --> E[paGating Unit]
    E --> F[Gate Branch: Linear → Sigmoid]
    E --> G[Value Branch: Activation Function]
    F --> H[Alpha Parameter: α]
    G --> I[Element-wise Multiply]
    H --> I
    I --> J[Linear: fc_out]
    J --> K[Next Block/Output]
    
    subgraph "paGating Unit Detail"
        L[Input: h] --> M[gate = σ(W_g × h)]
        L --> N[value = activation(W_v × h)]
        M --> O[α × gate]
        N --> P[(1-α) × value]
        O --> Q[Gated Output]
        P --> Q
        Q --> R[α × gate + (1-α) × value]
    end
    
    style E fill:#e3f2fd
    style H fill:#fff3e0
    style I fill:#e8f5e8
``` 