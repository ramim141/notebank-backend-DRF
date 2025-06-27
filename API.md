# ব্যবহারকারী (User) সম্পর্কিত API ডকুমেন্টেশন

## ১. ভূমিকা

এই API ডকুমেন্টেশনটি ব্যবহারকারীদের নিবন্ধন, লগইন, প্রোফাইল পরিচালনা এবং পাসওয়ার্ড সম্পর্কিত কাজগুলি কভার করে।

## ২. Authentication

এই API-তে JWT (JSON Web Token) ব্যবহার করা হয়। লগইন করার পর প্রাপ্ত `access` টোকেনটি পরবর্তী API অনুরোধগুলিতে `Authorization` হেডার-এ `Bearer <token>` ফরম্যাটে পাঠাতে হবে।

## ৩. বেস URL

`/api/users/`

---

### 3.1. ব্যবহারকারী নিবন্ধন (User Registration)

*   **URL:** `/api/users/register/`
*   **HTTP Method:** `POST`
*   **Authentication:** `AllowAny`
*   **Description:** নতুন ব্যবহারকারী নিবন্ধন করার জন্য। একটি ভেরিফিকেশন ইমেল পাঠানো হতে পারে (যদি ইমেল প্রদান করা হয়)।

*   **Request Body JSON:**
    ```json
    {
        "username": "newuser",
        "email": "user@example.com",
        "password": "StrongPassword123!",
        "password2": "StrongPassword123!",
        "first_name": "John",       // Optional
        "last_name": "Doe",         // Optional
        "student_id": "123-456-789", // Required (Format: XXX-XXX-XXX)
        "department": 1,            // Optional (Department ID)
        "batch": "2020",            // Optional
        "section": "A"              // Optional
    }
    ```

*   **Successful Response JSON (201 Created):**
    ```json
    {
        "user": {
            "id": 1,
            "username": "newuser",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_email_verified": false,
            "student_id": "123-456-789",
            "department": null,         // Or the ID of the department if provided
            "department_name": null,    // Or the name of the department if provided
            "batch": null,              // Or the provided batch
            "section": null,            // Or the provided section
            "profile_picture_url": null,
            "bio": null,
            "mobile_number": null,
            "university": null,
            "website": null,
            "birthday": null,
            "gender": null,
            "skills": []
        },
        "message": "User registered successfully. A verification email has been sent."
    }
    ```
    *(Note: If an email is provided and a verification token is generated, a verification email will be sent. The message will reflect this. If no email is provided, a simpler success message will be shown.)*

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "email": ["A user with that email already exists."],
        // OR
        "student_id": ["A user with this Student ID already exists."],
        // OR
        "password": ["Password fields didn't match."],
        // OR
        "password": ["Password is too weak."],
        // OR
        "username": ["This field is required."],
        // OR
        "student_id": ["Student ID must be in the format: 'XXX-XXX-XXX' (e.g., 222-115-141)."]
    }
    ```

---

### 3.2. ব্যবহারকারী লগইন (User Login - JWT Token Generation)

*   **URL:** `/api/users/login/`
*   **HTTP Method:** `POST`
*   **Authentication:** `AllowAny`
*   **Description:** ব্যবহারকারীর credential (username/email এবং password) যাচাই করে JWT অ্যাক্সেস এবং রিফ্রেশ টোকেন প্রদান করে।

*   **Request Body JSON:**
    ```json
    {
        "username": "existinguser",
        "password": "UserPassword123!"
    }
    ```

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "access": "your_access_token_here",
        "refresh": "your_refresh_token_here",
        "user": {
            "id": 1,
            "username": "existinguser",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_email_verified": true,
            "student_id": "123-456-789",
            "department": 1, // Department ID
            "department_name": "Computer Science", // Department Name
            "batch": "2020",
            "section": "A",
            "profile_picture_url": "http://localhost:8000/media/profile_pics/user_1/profile.jpg",
            "bio": "Software engineer.",
            "mobile_number": "+8801XXXXXXXXX",
            "university": "Example University",
            "website": "http://example.com",
            "birthday": "1999-05-15",
            "gender": "M",
            "skills": ["Python", "Django"]
        }
    }
    ```

*   **Error Response JSON (401 Unauthorized):**
    ```json
    {
        "detail": "No active account found with the given credentials"
    }
    ```

---

### 3.3. টোকেন রিফ্রেশ (Token Refresh)

*   **URL:** `/api/users/token/refresh/`
*   **HTTP Method:** `POST`
*   **Authentication:** `AllowAny`
*   **Description:** রিফ্রেশ টোকেন ব্যবহার করে একটি নতুন অ্যাক্সেস টোকেন তৈরি করে।

*   **Request Body JSON:**
    ```json
    {
        "refresh": "your_refresh_token_here"
    }
    ```

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "access": "new_access_token_here"
    }
    ```

*   **Error Response JSON (401 Unauthorized):**
    ```json
    {
        "detail": "Token is invalid or expired"
    }
    ```

---

### 3.4. ব্যবহারকারীর প্রোফাইল পুনরুদ্ধার ও আপডেট (User Profile Retrieval & Update)

*   **URL:** `/api/users/profile/`
*   **HTTP Method:** `GET` (Retrieve), `PATCH` / `PUT` (Update)
*   **Authentication:** `IsAuthenticated`
*   **Description:** লগইন করা ব্যবহারকারীর প্রোফাইল ডেটা পুনরুদ্ধার (GET) বা আপডেট (PATCH/PUT) করার জন্য।

*   **Request Body JSON (for PATCH/PUT):**
    ```json
    {
        "first_name": "Jon",       // Optional
        "last_name": "Doe",        // Optional
        "profile_picture": "base64_encoded_image_data", // Optional (Base64 encoded image string or file upload)
        "bio": "Updated bio.",     // Optional
        "mobile_number": "+8801XXXXXXXXX", // Optional
        "university": "New Example University", // Optional
        "website": "http://newexample.com", // Optional
        "birthday": "1999-05-15",   // Optional (YYYY-MM-DD)
        "gender": "O",             // Optional (M, F, O)
        "skills": ["Python", "Django", "JavaScript"], // Optional (List of skills)
        "department": 2            // Optional (Department ID)
    }
    ```
    *(Note: `username`, `email`, `student_id`, `is_email_verified` are read-only and cannot be updated via this endpoint. `profile_picture` can be updated or set to `""` to remove it.)*

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "id": 1,
        "username": "existinguser",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_email_verified": true,
        "student_id": "123-456-789",
        "department": 1,
        "department_name": "Computer Science",
        "batch": "2020",
        "section": "A",
        "profile_picture_url": "http://localhost:8000/media/profile_pics/user_1/profile.jpg",
        "bio": "Updated bio.",
        "mobile_number": "+8801XXXXXXXXX",
        "university": "New Example University",
        "website": "http://newexample.com",
        "birthday": "1999-05-15",
        "gender": "O",
        "skills": ["Python", "Django", "JavaScript"]
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "non_field_errors": ["The two new password fields didn't match."], // Example for change password
        // OR
        "email": ["Enter a valid email address."],
        // OR
        "student_id": ["Student ID must be in the format: 'XXX-XXX-XXX' (e.g., 222-115-141)."]
    }
    ```

---

### 3.5. পাসওয়ার্ড পরিবর্তন (Change Password)

*   **URL:** `/api/users/change-password/`
*   **HTTP Method:** `PUT` (or `PATCH`)
*   **Authentication:** `IsAuthenticated`
*   **Description:** লগইন করা ব্যবহারকারীর বর্তমান পাসওয়ার্ড ব্যবহার করে নতুন পাসওয়ার্ড সেট করার জন্য।

*   **Request Body JSON:**
    ```json
    {
        "old_password": "UserPassword123!",
        "new_password": "NewStrongPassword456!",
        "new_password2": "NewStrongPassword456!"
    }
    ```

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "detail": "Password updated successfully"
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "old_password": ["Your old password was entered incorrectly. Please enter it again."],
        // OR
        "new_password": ["The two new password fields didn't match."],
        // OR
        "new_password": ["Password is too weak."]
    }
    ```

---

### 3.6. ইমেল ভেরিফিকেশন (Email Verification)

*   **URL:** `/api/users/verify-email/<uuid:token>/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **URL Parameters:**
    *   `token`: ভেরিফিকেশন ইমেলের মাধ্যমে পাঠানো UUID টোকেন।

*   **Description:** ব্যবহারকারীর ইমেল ঠিকানা যাচাই করার জন্য।

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "detail": "Email verified successfully."
    }
    ```
    *(Note: If the email is already verified, a `200 OK` response with `{"detail": "Email already verified."}` will be returned.)*

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "detail": "Invalid or expired verification token."
    }
    ```
*   **Error Response JSON (500 Internal Server Error):**
    ```json
    {
        "detail": "An error occurred during email verification."
    }
    ```

---

### 3.7. পাসওয়ার্ড রিসেট অনুরোধ (Password Reset Request)

*   **URL:** `/api/users/password-reset/`
*   **HTTP Method:** `POST`
*   **Authentication:** `AllowAny`
*   **Description:** ব্যবহারকারীর পাসওয়ার্ড রিসেট করার জন্য একটি অনুরোধ শুরু করে এবং একটি রিসেট লিঙ্ক ইমেল করে।

*   **Request Body JSON:**
    ```json
    {
        "email": "user@example.com"
    }
    ```

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "detail": "Password reset email has been sent. Please check your inbox."
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "email": ["No user is associated with this email address."]
    }
    ```
*   **Error Response JSON (500 Internal Server Error):**
    ```json
    {
        "detail": "An error occurred while attempting to send the password reset email. Please try again later."
    }
    ```
    *(Note: This endpoint relies on `FRONTEND_URL` being set in `settings.py` to construct the password reset link.)*

---

### 3.8. পাসওয়ার্ড রিসেট নিশ্চিতকরণ (Password Reset Confirmation)

*   **URL:** `/api/users/password-reset-confirm/<str:uidb64>/<str:token>/`
*   **HTTP Method:** `POST`
*   **Authentication:** `AllowAny`
*   **URL Parameters:**
    *   `uidb64`: Base64 এনকোড করা ব্যবহারকারীর আইডি।
    *   `token`: পাসওয়ার্ড রিসেট টোকেন।

*   **Description:** পাসওয়ার্ড রিসেট লিঙ্কে প্রাপ্ত টোকেন ব্যবহার করে ব্যবহারকারীর পাসওয়ার্ড রিসেট করে।

*   **Request Body JSON:**
    ```json
    {
        "new_password1": "NewStrongPassword456!",
        "new_password2": "NewStrongPassword456!"
    }
    ```

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "detail": "Password has been reset successfully."
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "new_password2": ["The two password fields didn't match."],
        // OR
        "detail": "The reset link was invalid or has expired. Please request a new one."
    }
    ```

---

### 3.9. ব্যবহারকারীর সাথে যুক্ত নোটস (User's Linked Notes)

*   **URL:** `/api/users/user-activity/`
*   **HTTP Method:** `GET`
*   **Authentication:** `IsAuthenticated`
*   **Description:** লগইন করা ব্যবহারকারীর পছন্দের (liked) এবং বুকমার্ক করা নোটগুলি একটি পেজিনেটেড লিস্ট হিসাবে প্রদান করে।
*   **Query Parameters (Optional):**
    *   `category_name`: নোটগুলির বিভাগ অনুসারে ফিল্টার করার জন্য (e.g., `?category_name=Mathematics`)
    *   `page`: পেজিনেশন এর জন্য পেজ নম্বর (e.g., `?page=2`)

*   **Successful Response JSON (200 OK - Paginated List of Notes):**
    ```json
    {
        "count": 10,
        "next": "http://localhost:8000/api/users/user-activity/?page=2",
        "previous": null,
        "results": [
            {
                "id": 5,
                "title": "Introduction to Calculus",
                "description": "A comprehensive introduction to calculus concepts.",
                "uploader": {
                    "id": 1,
                    "username": "existinguser",
                    "profile_picture_url": "...",
                    "student_id": "123-456-789",
                    "department_name": "Mathematics"
                },
                "department": "Mathematics",
                "course": "Calculus I",
                "category": "Notes",
                "tags": ["calculus", "math", "intro"],
                "created_at": "2023-10-27T10:30:00Z",
                "updated_at": "2023-10-27T10:30:00Z",
                "likes_count": 15,
                "bookmarks_count": 5,
                "star_ratings_count": 3,
                "average_star_rating": 4.2,
                "is_liked_by_current_user": true, // Annotated field
                "is_bookmarked_by_current_user": true // Annotated field
            },
            // ... other notes
        ]
    }
    ```
    *(Note: This endpoint uses `UserLinkedNotesViewSet`. It also includes annotated fields `is_liked_by_current_user` and `is_bookmarked_by_current_user` based on the logged-in user.)*

---

### 3.10. ব্যবহারকারীর বুকমার্ক করা নোটস (User's Bookmarked Notes)

*   **URL:** `/api/users/user-activity/bookmarked-notes/`
*   **HTTP Method:** `GET`
*   **Authentication:** `IsAuthenticated`
*   **Description:** ব্যবহারকারীর বুকমার্ক করা সমস্ত নোটের একটি পেজিনেটেড তালিকা প্রদান করে।
*   **Query Parameters (Optional):**
    *   `category_name`: নোটগুলির বিভাগ অনুসারে ফিল্টার করার জন্য (e.g., `?category_name=Physics`)

*   **Successful Response JSON (200 OK - Paginated List of Bookmarked Notes):**
    ```json
    {
        "count": 5,
        "next": null,
        "previous": null,
        "results": [
            // ... same note structure as above, but only bookmarked notes
            {
                "id": 10,
                "title": "Quantum Mechanics Basics",
                "description": "Fundamental principles of quantum mechanics.",
                "uploader": { ... },
                "department": "Physics",
                "course": "Quantum Physics",
                "category": "Notes",
                "tags": ["physics", "quantum"],
                "created_at": "2023-11-15T14:00:00Z",
                "updated_at": "2023-11-15T14:00:00Z",
                "likes_count": 20,
                "bookmarks_count": 8,
                "star_ratings_count": 4,
                "average_star_rating": 4.5,
                "is_liked_by_current_user": false,
                "is_bookmarked_by_current_user": true
            },
            // ... other bookmarked notes
        ]
    }
    ```

---

### 3.11. ব্যবহারকারীর লাইক করা নোটস (User's Liked Notes)

*   **URL:** `/api/users/user-activity/liked-notes/`
*   **HTTP Method:** `GET`
*   **Authentication:** `IsAuthenticated`
*   **Description:** ব্যবহারকারীর লাইক করা সমস্ত নোটের একটি পেজিনেটেড তালিকা প্রদান করে।
*   **Query Parameters (Optional):**
    *   `category_name`: নোটগুলির বিভাগ অনুসারে ফিল্টার করার জন্য (e.g., `?category_name=Chemistry`)

*   **Successful Response JSON (200 OK - Paginated List of Liked Notes):**
    ```json
    {
        "count": 12,
        "next": "http://localhost:8000/api/users/user-activity/liked-notes/?page=2",
        "previous": null,
        "results": [
            // ... same note structure as above, but only liked notes
            {
                "id": 7,
                "title": "Organic Chemistry Reactions",
                "description": "Common reactions in organic chemistry.",
                "uploader": { ... },
                "department": "Chemistry",
                "course": "Organic Chemistry II",
                "category": "Notes",
                "tags": ["chemistry", "organic"],
                "created_at": "2023-10-20T09:00:00Z",
                "updated_at": "2023-10-20T09:00:00Z",
                "likes_count": 25,
                "bookmarks_count": 7,
                "star_ratings_count": 5,
                "average_star_rating": 4.8,
                "is_liked_by_current_user": true,
                "is_bookmarked_by_current_user": false
            },
            // ... other liked notes
        ]
    }
    ```

---

### 3.12. সাইট স্ট্যাটস (Site Stats)

*   **URL:** `/api/users/site-stats/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** সাইটের সামগ্রিক পরিসংখ্যান (মোট ব্যবহারকারী, নোট, কোর্স, বিভাগ) প্রদান করে।

*   **Successful Response JSON (200 OK):**
    ```json
    {
        "total_users": 1500,
        "total_notes": 5000,
        "total_courses": 50,
        "total_departments": 10
    }
    ```

---




# `notes` অ্যাপের API ডকুমেন্টেশন

এই ডকুমেন্টেশনটি `notes` অ্যাপের বিভিন্ন রিসোর্স যেমন - ফ্যাকাল্টি, বিভাগ, কোর্স, নোট, রেটিং, মন্তব্য ইত্যাদি পরিচালনার জন্য API এন্ডপয়েন্টগুলির বর্ণনা প্রদান করে।

---

## ১. বেস URL

`/api/notes/`

---

### ১.১. ফ্যাকাল্টি (Faculty) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/faculties/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** সকল ফ্যাকাল্টির একটি পঠনযোগ্য তালিকা প্রদান করে।
*   **Response Fields:**
    *   `id`: ফ্যাকাল্টির ইউনিক আইডি।
    *   `name`: ফ্যাকাল্টির পুরো নাম।
    *   `department`: ফ্যাকাল্টির বিভাগের আইডি।
    *   `email`: ফ্যাকাল্টির ইমেল ঠিকানা।
*   **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "Dr. A. K. M. Fazlul Haque",
            "department": 1,
            "email": "fazlul.haque@example.com"
        },
        // ... other faculties
    ]
    ```

---

### ১.২. নোট ক্যাটাগরি (Note Category) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/categories/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** উপলব্ধ সকল নোট ক্যাটাগরির একটি পঠনযোগ্য তালিকা প্রদান করে।
*   **Response Fields:**
    *   `id`: ক্যাটাগরির ইউনিক আইডি।
    *   `name`: ক্যাটাগরির নাম (যেমন: "Lecture Notes")।
    *   `description`: ক্যাটাগরির সংক্ষিপ্ত বর্ণনা (ঐচ্ছিক)।
*   **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "Lecture Notes",
            "description": "Notes taken during lectures."
        },
        // ... other categories
    ]
    ```

---

### ১.৩. বিভাগ (Department) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/departments/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** সকল বিভাগের একটি পঠনযোগ্য তালিকা প্রদান করে।
*   **Response Fields:**
    *   `id`: বিভাগের ইউনিক আইডি।
    *   `name`: বিভাগের নাম।
*   **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "Computer Science and Engineering"
        },
        // ... other departments
    ]
    ```

---

### ১.৪. কোর্স (Course) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/courses/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** সকল কোর্সের একটি পঠনযোগ্য তালিকা প্রদান করে।
*   **Query Parameters (Optional):**
    *   `department`: নির্দিষ্ট বিভাগের কোর্স ফিল্টার করার জন্য (e.g., `?department=1`)
*   **Response Fields:**
    *   `id`: কোর্সের ইউনিক আইডি।
    *   `name`: কোর্সের নাম।
    *   `department`: এই কোর্সের সাথে সম্পর্কিত বিভাগের আইডি।
    *   `department_name`: এই কোর্সের সাথে সম্পর্কিত বিভাগের নাম।
*   **Example Response:**
    ```json
    [
        {
            "id": 101,
            "name": "Introduction to Programming",
            "department": 1,
            "department_name": "Computer Science and Engineering"
        },
        // ... other courses
    ]
    ```

---

### ১.৫. নোট (Note) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/`
*   **HTTP Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
*   **Authentication & Permissions:**
    *   `GET` (list, retrieve): `AllowAny`
    *   `POST` (create): `IsAuthenticated`
    *   `PUT`, `PATCH`, `DELETE` (update, destroy): `IsAuthenticated` & `IsOwnerOrReadOnly`
*   **Description:** নোট আপলোড, দেখা, আপডেট, ডিলিট, লাইক, বুকমার্ক এবং ডাউনলোড করার জন্য।

*   **Query Parameters (for `GET /api/notes/`):**
    *   `category__name`: ক্যাটাগরি নাম দিয়ে ফিল্টার (exact, icontains)
    *   `department__name`: বিভাগ নাম দিয়ে ফিল্টার (exact, icontains)
    *   `course__name`: কোর্স নাম দিয়ে ফিল্টার (exact, icontains)
    *   `semester`: সেমিস্টার দিয়ে ফিল্টার (exact, icontains)
    *   `uploader__username`: আপলোডার ইউজারনেম দিয়ে ফিল্টার (exact)
    *   `uploader__student_id`: আপলোডার স্টুডেন্ট আইডি দিয়ে ফিল্টার (exact)
    *   `tags__name`: ট্যাগ নাম দিয়ে ফিল্টার (exact, in)
    *   `is_approved`: অনুমোদিত স্ট্যাটাস দিয়ে ফিল্টার (exact)
    *   `search`: টাইটেল, ডেসক্রিপশন, ট্যাগ, কোর্স, বিভাগ বা ফ্যাকাল্টির নাম দিয়ে সার্চ।
    *   `ordering`: সর্টিংয়ের জন্য (e.g., `created_at`, `download_count`, `average_rating`, `title`)

*   **Request Body JSON (for `POST /api/notes/`):**
    ```json
    {
        "title": "Introduction to Algorithms",
        "description": "Detailed notes on fundamental algorithms.",
        "file": "base64_encoded_file_data_or_file_upload", // Required
        "category": 1, // Required (Category ID)
        "course": 101, // Optional (Course ID)
        "department": 1, // Optional (Department ID)
        "faculty": 1, // Optional (Faculty ID)
        "semester": "Fall 2023", // Optional
        "tags": ["algorithms", "data structures", "cs"] // Optional
    }
    ```

*   **Successful Response JSON (201 Created for POST):**
    ```json
    {
        "message": "Note submitted, wait for admin approval.",
        "note": {
            "id": 5,
            "uploader": 1,
            "uploader_username": "existinguser",
            "uploader_first_name": "John",
            "uploader_last_name": "Doe",
            "uploader_student_id": "123-456-789",
            "uploader_department": "Computer Science and Engineering",
            "title": "Introduction to Algorithms",
            "description": "Detailed notes on fundamental algorithms.",
            "file_url": "http://localhost:8000/media/notes/user_1/algo_notes.pdf",
            "file": "notes/user_1/algo_notes.pdf", // Might be read-only in GET response
            "faculty": 1,
            "faculty_name": "Dr. A. K. M. Fazlul Haque",
            "course": 101,
            "category": 1,
            "category_name": "Lecture Notes",
            "department": 1,
            "course_name": "Introduction to Programming",
            "department_name": "Computer Science and Engineering",
            "semester": "Fall 2023",
            "tags": ["algorithms", "data structures", "cs"],
            "is_approved": false,
            "download_count": 0,
            "average_rating": 0.0,
            "likes_count": 0,
            "is_liked_by_current_user": false,
            "bookmarks_count": 0,
            "is_bookmarked_by_current_user": false,
            "star_ratings": [],
            "comments": [],
            "created_at": "2023-11-15T10:00:00Z",
            "updated_at": "2023-11-15T10:00:00Z"
        }
    }
    ```

*   **Successful Response JSON (200 OK for GET, PUT, PATCH):**
    ```json
    {
        "id": 5,
        "uploader": 1,
        "uploader_username": "existinguser",
        "uploader_first_name": "John",
        "uploader_last_name": "Doe",
        "uploader_student_id": "123-456-789",
        "uploader_department": "Computer Science and Engineering",
        "title": "Introduction to Algorithms",
        "description": "Detailed notes on fundamental algorithms.",
        "file_url": "http://localhost:8000/media/notes/user_1/algo_notes.pdf",
        "file": "notes/user_1/algo_notes.pdf",
        "faculty": 1,
        "faculty_name": "Dr. A. K. M. Fazlul Haque",
        "course": 101,
        "category": 1,
        "category_name": "Lecture Notes",
        "department": 1,
        "course_name": "Introduction to Programming",
        "department_name": "Computer Science and Engineering",
        "semester": "Fall 2023",
        "tags": ["algorithms", "data structures", "cs"],
        "is_approved": true,
        "download_count": 5,
        "average_rating": 4.5,
        "likes_count": 10,
        "is_liked_by_current_user": true,
        "bookmarks_count": 2,
        "is_bookmarked_by_current_user": false,
        "star_ratings": [ ... ],
        "comments": [ ... ],
        "created_at": "2023-11-15T10:00:00Z",
        "updated_at": "2023-11-15T12:30:00Z"
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "title": ["This field is required."],
        // OR
        "file": ["No file was submitted."],
        // OR
        "category": ["This field is required."],
        // OR
        "non_field_errors": ["You can only edit your own notes or notes approved by admin."]
    }
    ```

#### **১.৫.১. নোট ডাউনলোড (Note Download)**

*   **URL:** `/api/notes/{note_id}/download/`
*   **HTTP Method:** `GET`
*   **Authentication:** `IsAuthenticated`
*   **Description:** নোটের ডাউনলোড কাউন্ট বৃদ্ধি করে এবং ফাইল ডাউনলোডের URL প্রদান করে।
*   **Response:**
    ```json
    {
        "detail": "Download initiated (count incremented). Please use the file_url to download.",
        "file_url": "http://localhost:8000/media/notes/user_1/algo_notes.pdf",
        "download_count": 6
    }
    ```

#### **১.৫.২. নোট লাইক/আনলাইক (Toggle Note Like/Unlike)**

*   **URL:** `/api/notes/{note_id}/toggle-like/`
*   **HTTP Method:** `POST`
*   **Authentication:** `IsAuthenticated`
*   **Description:** একটি নোটে লাইক যোগ বা অপসারণ করে।
*   **Response:**
    ```json
    {
        "message": "Note liked successfully.",
        "liked": true,
        "likes_count": 11
    }
    ```

#### **১.৫.৩. নোট বুকমার্ক/আনবুকমার্ক (Toggle Note Bookmark/Unbookmark)**

*   **URL:** `/api/notes/{note_id}/toggle-bookmark/`
*   **HTTP Method:** `POST`
*   **Authentication:** `IsAuthenticated`
*   **Description:** একটি নোটে বুকমার্ক যোগ বা অপসারণ করে।
*   **Response:**
    ```json
    {
        "message": "Note bookmarked successfully.",
        "bookmarked": true,
        "bookmarks_count": 3
    }
    ```

#### **১.৫.৪. ব্যবহারকারীর আপলোড করা নোটসমূহ (User's Uploaded Notes)**

*   **URL:** `/api/notes/my-notes/`
*   **HTTP Method:** `GET`
*   **Authentication:** `IsAuthenticated`
*   **Description:** বর্তমানে লগইন করা ব্যবহারকারীর আপলোড করা সমস্ত নোটের একটি পেজিনেটেড তালিকা প্রদান করে।
*   **Query Parameters (Optional):**
    *   `page`: পেজিনেশন এর জন্য পেজ নম্বর (e.g., `?page=2`)
*   **Response:**
    ```json
    {
        "count": 5,
        "next": null,
        "previous": null,
        "results": [
            // List of notes similar to GET /api/notes/, but only for the current user
            // Includes fields like id, title, description, average_rating, likes_count, etc.
        ]
    }
    ```

---

### ১.৬. স্টার রেটিং (Star Rating) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/star-ratings/`
*   **HTTP Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
*   **Authentication:** `IsAuthenticatedOrReadOnly`
*   **Permissions:** `IsRatingOrCommentOwnerOrReadOnly`
*   **Description:** একটি নোটের জন্য স্টার রেটিং যুক্ত, দেখা, আপডেট বা মুছে ফেলার জন্য। একজন ব্যবহারকারী একটি নোটে একবারই রেটিং দিতে পারে।

*   **Request Body JSON (for `POST`):**
    ```json
    {
        "note": 5, // Required (Note ID)
        "stars": 5 // Required (1-5)
    }
    ```

*   **Successful Response JSON (201 Created for POST):**
    ```json
    {
        "id": 10,
        "user": 1,
        "user_username": "existinguser",
        "user_first_name": "John",
        "user_last_name": "Doe",
        "user_student_id": "123-456-789",
        "stars": 5,
        "created_at": "2023-11-15T11:00:00Z",
        "updated_at": "2023-11-15T11:00:00Z",
        "note": 5
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "note": ["This field is required to create a rating."],
        // OR
        "stars": ["This field is required."],
        // OR
        "detail": "You have already rated this note. You can update your existing rating by sending a PUT/PATCH request to its ID."
    }
    ```

---

### ১.৭. মন্তব্য (Comment) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/comments/`
*   **HTTP Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
*   **Authentication:** `IsAuthenticatedOrReadOnly`
*   **Permissions:** `IsRatingOrCommentOwnerOrReadOnly`
*   **Description:** একটি নোটের জন্য মন্তব্য যুক্ত, দেখা, আপডেট বা মুছে ফেলার জন্য। একজন ব্যবহারকারী একটি নোটে একবারই মন্তব্য করতে পারে।

*   **Request Body JSON (for `POST`):**
    ```json
    {
        "note": 5, // Required (Note ID)
        "text": "Very helpful notes, thank you!"
    }
    ```

*   **Successful Response JSON (201 Created for POST):**
    ```json
    {
        "id": 20,
        "user": 1,
        "user_username": "existinguser",
        "user_first_name": "John",
        "user_last_name": "Doe",
        "user_student_id": "123-456-789",
        "text": "Very helpful notes, thank you!",
        "created_at": "2023-11-15T11:30:00Z",
        "updated_at": "2023-11-15T11:30:00Z",
        "note": 5
    }
    ```

*   **Error Response JSON (400 Bad Request):**
    ```json
    {
        "note": ["This field is required to create a comment."],
        // OR
        "text": ["This field is required."],
        // OR
        "detail": "You have already commented on this note. You can update your existing comment by sending a PUT/PATCH request to its ID."
    }
    ```

---

### ১.৮. নোট রিকোয়েস্ট (Note Request) সম্পর্কিত এন্ডপয়েন্ট

*   **URL:** `/api/notes/note-requests/`
*   **HTTP Methods:** `GET`, `POST`
*   **Authentication:** `IsAuthenticated`
*   **Description:** লগইন করা ব্যবহারকারীর জন্য নোট রিকোয়েস্ট তৈরি বা দেখার জন্য।

*   **Request Body JSON (for `POST`):**
    ```json
    {
        "course_name": "Advanced Database Systems",
        "department_name": "Computer Science and Engineering",
        "message": "Need notes for advanced database systems, especially on indexing techniques."
    }
    ```

*   **Successful Response JSON (201 Created for POST):**
    ```json
    {
        "id": 3,
        "user": 1,
        "user_username": "existinguser",
        "user_full_name": "John Doe",
        "user_student_id": "123-456-789",
        "course_name": "Advanced Database Systems",
        "department_name": "Computer Science and Engineering",
        "message": "Need notes for advanced database systems, especially on indexing techniques.",
        "status": "PENDING",
        "created_at": "2023-11-15T12:00:00Z"
    }
    ```

*   **Successful Response JSON (200 OK for GET):**
    ```json
    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 3,
                "user": 1,
                "user_username": "existinguser",
                "user_full_name": "John Doe",
                "user_student_id": "123-456-789",
                "course_name": "Advanced Database Systems",
                "department_name": "Computer Science and Engineering",
                "message": "Need notes for advanced database systems, especially on indexing techniques.",
                "status": "PENDING",
                "created_at": "2023-11-15T12:00:00Z"
            }
            // ... other requests by the user
        ]
    }
    ```

---

### ১.৯. কন্ট্রিবিউটর (Contributor) সম্পর্কিত এন্ডপয়েন্ট

*   **URL Prefix:** `/api/notes/contributors/`
*   **HTTP Method:** `GET`
*   **Authentication:** `AllowAny`
*   **Description:** ব্যবহারকারীদের কন্ট্রিবিউশন প্রোফাইলের একটি পঠনযোগ্য তালিকা প্রদান করে। ডেটা `Contributor` মডেল থেকে আসে।
*   **Query Parameters (Optional):**
    *   `department_name`: বিভাগের নাম দিয়ে ফিল্টার (e.g., `?department_name=Computer Science and Engineering`)
*   **Response Fields:**
    *   `full_name`: ব্যবহারকারীর পুরো নাম।
    *   `batch_with_section`: ব্যবহারকারীর ব্যাচ ও সেকশন (e.g., "2020(A)")।
    *   `department_name`: ব্যবহারকারীর বিভাগের নাম।
    *   `email`: ব্যবহারকারীর ইমেল।
    *   `note_contribution_count`: ব্যবহারকারী কর্তৃক আপলোড করা অনুমোদিত নোটের সংখ্যা।
    *   `average_star_rating`: ব্যবহারকারীর নোটগুলির গড় রেটিং।
    *   `updated_at`: কন্ট্রিবিউটর প্রোফাইল আপডেটের সময়।
*   **Example Response:**
    ```json
    [
        {
            "full_name": "John Doe",
            "batch_with_section": "2020(A)",
            "department_name": "Computer Science and Engineering",
            "email": "john.doe@example.com",
            "note_contribution_count": 50,
            "average_star_rating": 4.5,
            "updated_at": "2023-11-15T12:30:00Z"
        },
        // ... other contributors
    ]
    ```

---