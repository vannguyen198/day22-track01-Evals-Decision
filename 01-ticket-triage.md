# Case 1 - Support Ticket Triage

## Mục tiêu

Case này giúp học viên luyện 4 câu hỏi nên bật ra ngay khi gặp một AI task:

- Cái gì deterministic và nên chấm bằng code?
- Cái gì cần semantic judgment và nên giao cho LLM judge hoặc human?
- Cái gì high-risk nên cần gate chặt hơn?
- Sai ở đâu thì cần escalation sang người thật?

Chỉ cần thiết kế eval ban đầu, không cần code full system.

Case này nối trực tiếp từ track **AI Customer Support Agent** ở Day 18/19, nhưng đổi góc nhìn từ **thiết kế trải nghiệm** sang **thiết kế eval**.

---

## 1. Bối cảnh

Một công ty SaaS B2B dùng AI để đọc ticket support mới và tạo output triage cho hệ thống nội bộ.

Output này không gửi trực tiếp cho khách hàng, nhưng nó được dùng để:

- phân loại ticket,
- đánh dấu mức độ gấp,
- route đến đúng team,
- quyết định có cần người thật nhảy vào hay không.

Nếu AI route sai, ticket có thể bị trễ, bỏ sót escalation, hoặc đẩy sai sang team không xử lý được.

---

## 2. Workflow logic (ASCII)

```text
Khách hàng gửi ticket hỗ trợ
    ↓
AI đọc:
- tiêu đề
- nội dung ticket
- loại khách hàng
    ↓
Hệ thống phải quyết định:
- đây là loại vấn đề gì?
- mức độ khẩn cấp ra sao?
- có cần người thật xử lý ngay không?
- ticket nên vào hàng của team nào?
    ↓
UI inbox nội bộ hiển thị:
- nhãn loại yêu cầu
- mức độ khẩn
- team phụ trách
- cờ "cần xử lý ngay"
- lý do tóm tắt
    ↓
Nếu khách doanh nghiệp + có dấu hiệu chặn công việc
    ↓
Đẩy lên hàng ưu tiên cao / escalation
```

---

## 3. UI hiển thị dự kiến (ASCII)

```text
+----------------------------------------------------------------+
| Hộp thư hỗ trợ nội bộ                                           |
+----------------------------------------------------------------+
| Ticket: T-002                                                   |
| Khách hàng: Công ty ABC (Enterprise)                            |
| Tiêu đề: Thanh toán lỗi, tài khoản bị khóa                      |
|----------------------------------------------------------------|
| AI gợi ý                                                        |
| - Loại yêu cầu: [ ? ]                                           |
| - Mức độ khẩn: [ ? ]                                            |
| - Team phụ trách: [ ? ]                                         |
| - Cần người xử lý ngay: [ ? ]                                   |
| - Lý do tóm tắt: [ .......................................... ] |
|----------------------------------------------------------------|
| Hàng đợi hiện tại: [ Bình thường ] hoặc [ Ưu tiên cao ]         |
+----------------------------------------------------------------+
```

Học viên cần tự đề xuất output contract tối thiểu phía sau để màn hình này hiển thị được.

---

## 4. Input mẫu

```json
{
  "ticket_id": "T-001",
  "subject": "Cannot login after password reset",
  "message": "I reset my password twice but still cannot log in. This is blocking my work.",
  "customer_tier": "enterprise"
}
```

Một input khác:

```json
{
  "ticket_id": "T-002",
  "subject": "URGENT: payment failed and account disabled",
  "message": "Our team is locked out because your billing system failed. Fix this now.",
  "customer_tier": "enterprise"
}
```

---

## 5. Business rules / operational rules

- Output phải đúng schema và đúng allowed enums.
- `confidence` phải nằm trong khoảng `0-1`.
- Nếu `customer_tier = enterprise` và `urgency` là `high` hoặc `critical`, `requires_human` phải bằng `true`.
- Ticket billing không được route sang `product_team`.
- Ticket có dấu hiệu “blocking work”, “locked out”, hoặc “account disabled” không nên bị đánh `low`.
- `reason_codes` phải phản ánh được nội dung ticket, không được bốc thêm sự thật không có trong input.

---

## 6. Ví dụ full luồng để hình dung nhanh

### Tình huống

Khách hàng doanh nghiệp nhắn vào kênh hỗ trợ:

```text
Chị ơi bên em reset mật khẩu 2 lần rồi mà tài khoản admin vẫn không vào được.
Bên em đang bị chặn công việc từ sáng.
```

### Data mẫu

- `customer_tier`: `enterprise`
- `account_name`: `Công ty Minh Phát Logistics`
- `previous_tickets_7d`: `0`
- `channel`: `Zalo OA`

### Workflow ASCII

```text
Khách nhắn vấn đề đăng nhập
    ↓
AI đọc nội dung + loại khách hàng
    ↓
AI phát hiện tín hiệu:
- login issue
- blocked work
- enterprise customer
    ↓
Hệ thống gợi ý:
- category = technical
- urgency = high hoặc critical
- requires_human = true
- route_to = technical_support
    ↓
UI nội bộ đẩy ticket lên hàng ưu tiên
    ↓
Nhân viên hỗ trợ xem lại rồi tiếp nhận
```

### UI trước khi AI xử lý (ASCII)

```text
+----------------------------------------------------------------+
| Hộp thư hỗ trợ nội bộ                                           |
+----------------------------------------------------------------+
| Ticket: T-115                                                   |
| Kênh: Zalo OA                                                   |
| Khách hàng: Minh Phát Logistics                                 |
|----------------------------------------------------------------|
| Nội dung khách nhắn:                                            |
| "Reset mật khẩu 2 lần rồi mà tài khoản admin vẫn không vào..."  |
|----------------------------------------------------------------|
| AI gợi ý: Chưa có                                               |
+----------------------------------------------------------------+
```

### UI sau khi AI xử lý (ASCII)

```text
+----------------------------------------------------------------+
| Hộp thư hỗ trợ nội bộ                                           |
+----------------------------------------------------------------+
| Ticket: T-115                                                   |
| Khách hàng: Minh Phát Logistics (Enterprise)                    |
|----------------------------------------------------------------|
| AI gợi ý                                                        |
| - Loại yêu cầu: Technical                                       |
| - Mức độ khẩn: High                                             |
| - Team phụ trách: Technical Support                             |
| - Cần người xử lý ngay: Có                                      |
| - Lý do tóm tắt: Lỗi đăng nhập đang chặn công việc              |
| - Hàng đợi: Ưu tiên cao                                         |
+----------------------------------------------------------------+
```

Ví dụ này giúp người đọc hình dung ngay:

- AI đang quyết định gì,
- quyết định nào hiển thị ra UI,
- và sai ở đâu thì ảnh hưởng vận hành.

---

## 7. Seed cases

Đây không phải full dataset. Đây chỉ là 3 seed cases để học viên hình dung phạm vi và failure modes.

### Seed A - Happy path

- `subject`: `Cannot login after password reset`
- Kỳ vọng: `category = technical`, `requires_human = true` nếu urgency đủ cao, route về `technical_support`

### Seed B - Ambiguous / low-info

- `subject`: `Help`
- `message`: `Please help asap`
- Kỳ vọng: AI không nên tự tin gán category quá mạnh; cần `unknown` hoặc route theo hướng cần review

### Seed C - High-risk / escalation

- `subject`: `URGENT: payment failed and account disabled`
- Kỳ vọng: `category = billing`, `urgency = critical`, `requires_human = true`, route về `billing_ops` hoặc `human_escalation`

---

## 8. Bạn phải đề xuất thêm 5 Dataset Edge Cases

Sau khi đọc seed cases ở trên, hãy đề xuất thêm 5 case cần đưa vào reference dataset version đầu.

Không cần nộp một bảng coverage riêng. Hãy chọn 5 case đại diện cho các lát cắt khác nhau, ví dụ: match rõ, thiếu tín hiệu, ambiguity, escalation, và regression.

1. Happy path:
2. Ambiguous input:
3. Missing information:
4. High-risk / escalation:
5. Regression case:

Với mỗi case, thêm 1 dòng ngắn giải thích:

- case này dùng để bắt failure gì?

---

## 9. Mock outcome để soi

Giả sử trên UI nội bộ, hệ thống hiển thị kết quả gợi ý như sau cho `T-002`:

```text
+----------------------------------------------------------------+
| Ticket: T-002                                                   |
| Khách hàng: Enterprise                                          |
|----------------------------------------------------------------|
| AI gợi ý                                                        |
| - Loại yêu cầu: Product question                                |
| - Mức độ khẩn: Medium                                           |
| - Team phụ trách: Support L1                                    |
| - Cần người xử lý ngay: Không                                   |
| - Lý do tóm tắt: Có vấn đề thanh toán                           |
| - Độ tin cậy: 0.91                                              |
+----------------------------------------------------------------+
```

Kết quả này trông có vẻ “ổn” nếu chỉ nhìn bề mặt, nhưng khả năng cao là sai về judgment vận hành.

---

## 10. Nhiệm vụ học viên

Hãy điền workbook bên dưới cho case này.

Không cần:

- viết eval runner,
- viết prompt judge thật,
- làm lại `User Input Grid` đầy đủ như bài test inputs hôm trước,
- tạo full dataset lớn,
- code full system.

Cần làm:

- chọn đúng nguồn chấm cho từng thành phần,
- viết các rule kiểm tra đủ cụ thể để có thể implement sau,
- đặt release gate có ý nghĩa vận hành,
- đề xuất 5 edge cases cần đưa vào reference dataset,
- và lập một pilot plan có thời gian + chi phí sơ bộ.

---

## 11. Bạn nên làm gì ở case 1?

Đây là case scaffold cao, nên cách làm tốt nhất là:

1. Đọc ví dụ full luồng trước để hiểu “một output tốt trông như thế nào”.
2. So mock outcome với ví dụ full luồng để thấy lỗi đang nằm ở đâu.
3. Nhìn từ UI để suy ra các field tối thiểu hệ thống phải có.
4. Điền `Eval Decision Map` trước, rồi mới quay lại viết các kiểm tra tự động và gate.

Case này thường **không bắt buộc phải có domain expert chuyên sâu**. Nếu chọn không cần expert, bạn vẫn phải giải thích vì sao human review vận hành là đủ.

---

## 12. Workbook

Lưu ý chung cho toàn bộ câu trả lời:

- Không chỉ điền đáp án ngắn.
- Với mỗi phần, hãy nêu cả **quyết định** và **lý do**.
- Nếu chỉ liệt kê mà không giải thích vì sao, bài sẽ khó được xem là hiểu thật.

### 1. Unit of Work

> Tôi chọn lát cắt công việc (Unit of Work) là: **Từ một ticket hỗ trợ đầu vào, AI phân tích và tạo ra một bộ gợi ý phân loại bao gồm loại yêu cầu, mức độ khẩn cấp, team phụ trách và đề xuất escalation.**

> Đây là đơn vị công việc đủ nhỏ để đánh giá vì nó có đầu vào (nội dung ticket) và đầu ra (bộ gợi ý) rất rõ ràng, có thể kiểm thử một cách độc lập cho từng ticket. Tuy nhiên, nó vẫn chứa rủi ro vận hành đáng kể vì nếu AI phân loại sai (ví dụ: đánh giá thấp mức độ khẩn của một khách hàng Enterprise), hậu quả trực tiếp là ticket bị xử lý chậm, sai quy trình, gây ảnh hưởng đến trải nghiệm của khách hàng và uy tín của công ty.

### 2. Quality Question

> **Câu hỏi chất lượng của tôi là: Với một ticket đầu vào, AI có phân biệt chính xác giữa các yêu cầu thông thường và các yêu cầu khẩn cấp cần escalation (đặc biệt là từ khách hàng enterprise), đồng thời đề xuất đúng team phụ trách để không làm trễ hoặc xử lý sai các vấn đề nghiêm trọng không?**
>
> Câu hỏi này quan trọng vì nếu AI thất bại, một ticket nghiêm trọng như "tài khoản bị khóa" của khách hàng lớn có thể bị đánh giá là "ưu tiên thấp" và gửi sai team. Điều này trực tiếp dẫn đến việc xử lý chậm trễ, vi phạm cam kết dịch vụ (SLA), làm suy giảm nghiêm trọng lòng tin của khách hàng và có thể gây ra tổn thất kinh doanh.

### 3. Output Contract tối thiểu

Dưới đây là các trường tối thiểu cần có trong Output Contract:

> - **`category` (string):**
>   - **Lý do:** Cần thiết để hiển thị `Loại yêu cầu` trên UI, quyết định `Team phụ trách` (ví dụ: "Billing" -> route cho team Billing), và là một trong những tiêu chí cốt lõi để đánh giá (eval) độ chính xác của AI.
> - **`urgency` (string):**
>   - **Lý do:** Dùng để hiển thị `Mức độ khẩn` trên UI, là yếu tố đầu vào quan trọng cho logic `escalation` (ví dụ: khách Enterprise + urgency "Critical" -> đẩy lên hàng ưu tiên), và là một tiêu chí eval quan trọng về an toàn.
> - **`route_to_team` (string):**
>   - **Lý do:** Đây là kết quả routing trực tiếp, hiển thị `Team phụ trách` trên UI. Việc route sai team là một lỗi vận hành nghiêm trọng, do đó đây là một trường bắt buộc phải có để eval.
> - **`requires_human_escalation` (boolean):**
>   - **Lý do:** Quyết định cờ `Cần người xử lý ngay` trên UI và trigger quy trình `escalation`. Đây là một cổng an toàn (safety gate) để đảm bảo các trường hợp khẩn cấp không bị bỏ sót, và là một tiêu chí eval cực kỳ quan trọng.
> - **`summary` (string):**
>   - **Lý do:** Hiển thị `Lý do tóm tắt` trên UI, giúp nhân viên hỗ trợ nắm nhanh bối cảnh. Chất lượng của tóm tắt (súc tích, không bịa đặt) là một tiêu chí eval quan trọng, thường được chấm bằng LLM hoặc con người.
> - **`confidence_score` (float):**
>   - **Lý do:** Cung cấp một tín hiệu về độ tin cậy của AI cho nhân viên hỗ trợ trên UI. Trong eval, nó giúp lọc ra các trường hợp AI không chắc chắn để con người review kỹ hơn.
> - **`reason_codes` (array of strings):**
>   - **Lý do:** Đây là một trường ở backend, không nhất thiết hiện trên UI, nhưng cực kỳ quan trọng cho việc eval và debug. Nó lưu lại các tín hiệu (ví dụ: `["locked_out", "enterprise_customer"]`) mà AI đã dựa vào để đưa ra quyết định, giúp kiểm tra logic của AI một cách tự động.

### 4. Eval Decision Map

| Thành phần cần chấm | Code | LLM | Human | Expert | Lý do |
| --- | :---: | :---: | :---: | :---: | --- |
| **1. Tuân thủ schema và enum** (`category`, `urgency`) | ✅ | | | | **Code** là cách nhanh, rẻ và đáng tin cậy nhất để kiểm tra xem output có đúng định dạng JSON và các giá trị có nằm trong danh sách cho phép không (ví dụ: `category` phải là "Billing"). |
| **2. Độ chính xác của `category`** | | ✅ | ✅ | | **LLM** có thể chấm ở quy mô lớn xem AI có hiểu đúng nội dung ticket để gán `category` không. **Human** (support lead) cần thiết để tạo bộ dữ liệu vàng (golden dataset) và kiểm định (calibrate) LLM judge. |
| **3. Độ chính xác của `urgency`** | | ✅ | ✅ | | Tương tự `category`, **LLM** có thể đọc các tín hiệu khẩn cấp. **Human** cần review các trường hợp rủi ro cao (ví dụ: khách hàng enterprise) và định nghĩa rubric (ví dụ: "tài khoản bị khóa" luôn là "Critical"). |
| **4. Quyết định `requires_human_escalation`** | ✅ | | ✅ | | **Code** có thể kiểm tra các quy tắc cứng (ví dụ: `urgency` là "Critical" thì `requires_human_escalation` phải là `true`). **Human** phải review các ca mà AI bỏ lỡ escalation (false negatives), vì đây là lỗi vận hành nghiêm trọng. |
| **5. Chất lượng của `summary`** | | ✅ | ✅ | | **LLM** rất phù hợp để đánh giá tóm tắt có súc tích, trung thực (không bịa đặt) và nắm bắt đúng ý chính không. **Human** cần chấm điểm các trường hợp phức tạp hoặc khi LLM không chắc chắn. |
| **6. Tính hợp lệ của `route_to_team`** | ✅ | | ✅ | | **Code** có thể kiểm tra xem `route_to_team` có hợp lệ dựa trên `category` không (ví dụ: `category: Billing` -> `route_to_team: Billing Ops`). **Human** cần xác nhận tính đúng đắn của logic routing này trong các trường hợp phức tạp. |

### 5. Kiểm tra tự động bằng code

- **Kiểm tra:** Output phải là một JSON hợp lệ và tuân thủ đúng schema đã định nghĩa (ví dụ: có đủ các trường `category`, `urgency`, `route_to_team`, `requires_human_escalation`).
  **Vì sao nên giao cho code:** Đây là kiểm tra cấu trúc cơ bản nhất. Code có thể xác thực schema một cách nhanh chóng, rẻ và đáng tin cậy. Bất kỳ lỗi nào ở bước này đều cho thấy AI đã thất bại ở mức độ cơ bản nhất.

- **Kiểm tra:** Giá trị của trường `category` và `urgency` phải nằm trong một danh sách các giá trị cho phép (enum).
  **Vì sao nên giao cho code:** Việc kiểm tra một giá trị có thuộc một tập hợp cố định hay không là một logic xác định (deterministic). Giao cho code đảm bảo AI không "bịa" ra một loại ticket hay mức độ khẩn cấp mới, gây lỗi cho các hệ thống phía sau.

- **Kiểm tra:** Nếu `customer_tier` là "enterprise" VÀ `urgency` là "high" hoặc "critical", thì `requires_human_escalation` phải là `true`.
  **Vì sao nên giao cho code:** Đây là một quy tắc nghiệp vụ cứng và cực kỳ quan trọng. Code có thể kiểm tra điều kiện này một cách chính xác tuyệt đối, đóng vai trò là một cổng an toàn (safety gate) để đảm bảo các khách hàng quan trọng không bị bỏ sót.

- **Kiểm tra:** Nếu `urgency` là "critical", thì `requires_human_escalation` phải là `true`.
  **Vì sao nên giao cho code:** Tương tự như trên, đây là một quy tắc an toàn cơ bản. Bất kỳ ticket nào được đánh giá là "critical" đều phải được người xử lý ngay lập tức.

- **Kiểm tra:** Trường `route_to_team` phải hợp lệ dựa trên `category` (ví dụ: `category: "Billing"` thì `route_to_team` không được là `"Product Team"`).
  **Vì sao nên giao cho code:** Logic routing có thể được định nghĩa trong một bản đồ (map) hoặc cấu hình. Code có thể dễ dàng tra cứu và xác nhận rằng việc định tuyến của AI tuân thủ logic này, ngăn chặn các lỗi chuyển nhầm team một cách ngớ ngẩn.

- **Kiểm tra:** Trường `summary` không được rỗng hoặc chỉ chứa khoảng trắng.
  **Vì sao nên giao cho code:** Việc kiểm tra một chuỗi có rỗng hay không là việc cơ bản của code. Rule này đảm bảo AI luôn cung cấp một lý do tóm tắt, dù chất lượng của nó sẽ được chấm bằng LLM/Human.

- **Kiểm tra:** Trường `confidence_score` phải là một số thực (float) trong khoảng từ 0.0 đến 1.0.
  **Vì sao nên giao cho code:** Đây là một kiểm tra kiểu dữ liệu và phạm vi số học đơn giản, đảm bảo dữ liệu luôn nhất quán.

- **Kiểm tra:** Nếu ticket chứa các từ khóa nhạy cảm như "locked out", "account disabled", "billing failed", thì `urgency` không được phép là "low".
  **Vì sao nên giao cho code:** Việc tìm kiếm từ khóa trong văn bản là một tác vụ xác định. Rule này tạo ra một lớp phòng vệ nữa để ngăn AI đánh giá thấp các vấn đề nghiêm trọng một cách rõ ràng.

### 6. Tiêu chí chấm bằng LLM

- **Tiêu chí:** Mức độ hợp lý của `urgency` (Mức độ khẩn c) có nắm bắt được tác động thực tế lên người dùng không?
  **Vì sao code không bắt tốt:** Mức độ khẩn cấp thường được thể hiện qua giọng văn và ngữ cảnh ("việc này đang chặn toàn bộ team của tôi") thay vì các từ khóa rõ ràng như "khẩn cấp". LLM có thể suy luận mức độ nghiêm trọng từ những mô tả tác động này, trong khi code thì không.

- **Tiêu chí:** Chất lượng của `summary` (Lý do tóm tắt) có trung thực và chỉ dựa trên thông tin trong ticket không (không bịa đặt)?
  **Vì sao code không bắt tốt:** Đây là bài toán kiểm tra tính trung thực (faithfulness/groundedness). Code không thể so sánh ngữ nghĩa giữa tóm tắt và văn bản gốc để phát hiện thông tin bịa đặt. LLM có thể đọc hiểu cả hai và xác định xem tóm tắt có suy ra những điều không có trong ticket hay không.

- **Tiêu chí:** Chất lượng của `summary` có đầy đủ, không bỏ sót các chi tiết quan trọng (ví dụ: khách hàng đã thử những gì, hậu quả là gì) không?
  **Vì sao code không bắt tốt:** Code không thể xác định được "chi tiết nào là quan trọng". LLM có thể đọc toàn bộ ticket, xác định các thành phần chính của vấn đề (vấn đề, tác động, các bước đã thử) và kiểm tra xem tóm tắt có bỏ sót thông tin nào gây ảnh hưởng đến việc xử lý hay không.

- **Tiêu chí:** Phát hiện đúng cảm xúc/thái độ của khách hàng (ví dụ: thất vọng, tức giận, mỉa mai).
  **Vì sao code không bắt tốt:** Cảm xúc rất đa dạng và tinh vi. Một câu nói như "Tuyệt vời, lại thêm một lỗi nữa" mang ý mỉa mai và tức giận, nhưng hệ thống dựa trên từ khóa có thể chấm nhầm là "tích cực". LLM được huấn luyện trên kho dữ liệu khổng lồ có thể nhận diện các sắc thái này tốt hơn nhiều.

- **Tiêu chí:** Phân loại đúng các ticket có nội dung mơ hồ, thiếu thông tin.
  **Vì sao code không bắt tốt:** Một ticket chỉ có nội dung "Cứu tôi với" không chứa từ khóa nào để phân loại. Code sẽ không biết phải làm gì. LLM có thể nhận ra sự thiếu thông tin này và đề xuất đúng `category` là `Clarification Needed` (Cần làm rõ), thay vì đoán bừa một loại yêu cầu nào đó.

### 7. Human / Expert Review

> **Người cần review là các Trưởng nhóm Hỗ trợ (Support Leads) hoặc các nhân viên hỗ trợ cấp cao (Senior Support Staff).** Họ là những người có kinh nghiệm nhất, hiểu rõ quy trình vận hành, cam kết dịch vụ (SLA) và có khả năng phán đoán các tình huống phức tạp.
>
> **Họ cần tập trung review các case sau:**
> 1.  **Các ca AI bỏ lỡ escalation (False Negatives):** Đây là lỗi nghiêm trọng nhất, ví dụ ticket "tài khoản bị khóa" của khách Enterprise nhưng AI không bật cờ `requires_human_escalation`.
> 2.  **Các ca AI có độ tin cậy thấp:** Khi `confidence_score` dưới một ngưỡng nhất định, cần người có kinh nghiệm xác nhận lại.
> 3.  **Các ca có sự mâu thuẫn:** Khi nhân viên hỗ trợ phải sửa lại đề xuất của AI. Việc review các case này giúp tìm ra điểm yếu trong logic của AI.
> 4.  **Một mẫu ngẫu nhiên các case "bình thường":** Để kiểm tra xem AI có đang âm thầm mắc lỗi hệ thống mà không bị phát hiện hay không.

Nếu chọn **có domain expert**, bạn phải làm thêm 2 phần dưới đây. Nếu **không cần domain expert**, hãy ghi `Không áp dụng` và giải thích 1 câu.

#### 7A. Màn hình cho Domain Expert (ASCII)

> Không áp dụng. Vì case này không yêu cầu domain expert chuyên sâu (như y tế, pháp lý), vai trò review được đảm nhiệm bởi các Support Leads. Do đó, không cần thiết kế một màn hình riêng cho một vai trò không tồn tại trong luồng này.

#### 7B. Tiêu chí review của Domain Expert

> **Không áp dụng.** Vì không cần domain expert, nên cũng không có bộ tiêu chí riêng cho vai trò này. Các tiêu chí đánh giá đã được bao phủ bởi các Support Leads trong vai trò human reviewer.

### 8. Release Gate

Một phiên bản AI mới sẽ bị **CHẶN (BLOCK)** phát hành nếu vi phạm bất kỳ điều kiện nào sau đây:

1.  **Không có lỗi nghiêm trọng (Zero P0/P1 Failures):**
    *   **Điều kiện:** `Số lượng lỗi P0 hoặc P1 > 0`.
    *   **Lý do:** Tuyệt đối không chấp nhận bất kỳ lỗi nào được phân loại là nghiêm trọng, ví dụ như bỏ sót escalation cho khách hàng Enterprise đang bị khóa tài khoản (lỗi P0), hoặc route sai một ticket khẩn cấp sang team không liên quan (lỗi P1).

2.  **Tỷ lệ tuân thủ schema tuyệt đối:**
    *   **Điều kiện:** `Tỷ lệ output tuân thủ schema < 100%`.
    *   **Lý do:** Output sai định dạng là lỗi cơ bản nhất và có thể làm sập các hệ thống tích hợp phía sau. Điều này phải luôn được đảm bảo tối đa.

3.  **Recall của việc Escalation phải cực cao:**
    *   **Điều kiện:** `Tỷ lệ phát hiện đúng các case cần escalation (Recall) < 98%`.
    *   **Lý do:** Bỏ sót một trường hợp cần xử lý khẩn cấp nguy hiểm hơn nhiều so với việc leo thang nhầm một vài trường hợp không khẩn cấp. Chúng ta phải tối ưu để bắt được gần như toàn bộ các ca nguy hiểm.

4.  **Không có hồi quy (regression) trên các case quan trọng:**
    *   **Điều kiện:** `Tỷ lệ pass trên bộ test hồi quy < 100%`.
    *   **Lý do:** Bất kỳ lỗi nào đã được sửa trong quá khứ và được đưa vào bộ test hồi quy đều không được phép tái diễn.

---

Phiên bản mới sẽ bị **CẢNH BÁO (WARN)** và cần người có thẩm quyền (ví dụ: Product Manager, Tech Lead) review thủ công trước khi quyết định phát hành:

1.  **Độ chính xác tổng thể không giảm quá sâu:**
    *   **Điều kiện:** `Độ chính xác của việc phân loại (category accuracy) < (phiên bản cũ - 3%)`.
    *   **Lý do:** Một sự sụt giảm nhẹ có thể chấp nhận được nếu phiên bản mới cải thiện ở các mặt quan trọng khác (như an toàn), nhưng sụt giảm quá nhiều là một dấu hiệu xấu.

2.  **Chi phí và độ trễ trong tầm kiểm soát:**
    *   **Điều kiện:** `Chi phí trung bình mỗi lượt phân tích > (phiên bản cũ * 1.2)` hoặc `Độ trễ P95 > (phiên bản cũ * 1.2)`.
    *   **Lý do:** Cần kiểm soát chi phí vận hành và đảm bảo trải nghiệm cho nhân viên hỗ trợ không bị chậm đi đáng kể.

### 9. Kế hoạch chạy thử và dự toán chi phí

Để trả lời các câu hỏi về độ chính xác, mức độ an toàn và tiềm năng của hướng đi này, tôi đề xuất một kế hoạch thử nghiệm (pilot) với các giả định và chi phí như sau:

**1. Các giả định:**
*   **Model sử dụng:** Google Gemini 1.5 Flash, một model nhanh, chi phí thấp, phù hợp cho việc phân loại và tóm tắt.
*   **Quy mô thử nghiệm:**
    *   **Bộ dữ liệu tham chiếu (Reference Dataset):** 100 tickets, bao gồm các ca happy path, mơ hồ, và rủi ro cao.
    *   **Số lần chạy lặp lại (Iterations):** 40 lần, tương ứng với các vòng lặp tinh chỉnh prompt, logic, và cấu hình hệ thống.
*   **Token trung bình mỗi ticket:**
    *   Input (prompt + nội dung ticket): ~500 tokens
    *   Output (JSON kết quả): ~150 tokens

**2. Dự toán chi phí:**

*   **Chi phí nhân sự (tính theo giờ công):**
    *   **PM / Thiết kế Eval (20 giờ):** Xây dựng bộ tiêu chí eval, thiết kế dataset, phân tích kết quả và đề xuất hướng đi tiếp theo.
    *   **Kỹ thuật (15 giờ):** Xây dựng và duy trì eval runner, tích hợp vào CI, đảm bảo các lần chạy được ghi nhận đúng.
    *   **Human Review (Support Leads - 22 giờ):**
        *   Tạo bộ dữ liệu vàng cho 100 cases (~8 giờ).
        *   Review các lỗi nghiêm trọng và các ca AI có độ tin cậy thấp qua 40 lần chạy (~14 giờ).
    *   **Domain Expert:** 0 giờ (không áp dụng cho case này).
    *   **Tổng giờ công:** 20 + 15 + 22 = **57 giờ**.

*   **Chi phí máy (API):**
    *   **Giá API (Gemini 1.5 Flash, on-demand):**
        *   Input: $0.35 / 1 triệu tokens
        *   Output: $1.05 / 1 triệu tokens
    *   **Tổng tokens:**
        *   Input: 100 cases * 40 lần chạy * 500 tokens = 2,000,000 tokens
        *   Output: 100 cases * 40 lần chạy * 150 tokens = 600,000 tokens
    *   **Tổng chi phí API:** (2 * $0.35) + (0.6 * $1.05) = $0.70 + $0.63 = **$1.33**.

**3. Tổng kết:**

*   **Tổng thời gian dự kiến:** Khoảng **1.5 tuần**, với các vai trò làm việc song song.
*   **Tổng chi phí (chỉ tính phần cứng/API):** **~ $2**. Chi phí nhân sự sẽ được tính theo lương nội bộ.

---

Tôi sử dụng giá API công khai của Google Cloud cho model Gemini 1.5 Flash tại thời điểm tháng 6/2026 để tính toán.

Với quy mô này, chi phí API là không đáng kể, gánh nặng chính nằm ở chi phí nhân sự (khoảng 57 giờ công). Kế hoạch này là đủ để chứng minh tính khả thi của giải pháp vì nó cho phép chúng ta:
1.  **Đo lường được độ chính xác:** Với 100 cases và 40 lần lặp, chúng ta có thể ra được các chỉ số về độ chính xác phân loại, recall của việc escalation.
2.  **Xác định được rủi ro:** Quá trình review của Support Leads sẽ giúp phát hiện các lỗi nghiêm trọng (false negatives) và các điểm yếu trong logic của AI.
3.  **Xây dựng được Release Gate:** Các kết quả từ pilot sẽ là cơ sở để định nghĩa các ngưỡng chất lượng cho `Release Gate` trước khi triển khai rộng hơn.

---
