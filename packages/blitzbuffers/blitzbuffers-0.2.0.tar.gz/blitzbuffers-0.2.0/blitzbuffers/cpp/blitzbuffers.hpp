
#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <iterator>
#include <optional>
#include <sstream>
#include <variant>
#include <vector>

#ifdef __cpp_lib_span
#include <span>
#endif

namespace blitzbuffers
{
    // https://en.cppreference.com/w/cpp/utility/variant/visit
    template <class... Ts>
    struct overloaded : Ts...
    {
        using Ts::operator()...;
    };

    // explicit deduction guide (not needed as of C++20)
    template <class... Ts>
    overloaded(Ts...) -> overloaded<Ts...>;

    // https://stackoverflow.com/questions/64017982/c-equivalent-of-rust-enums
    template <typename Val, typename... Ts>
    inline auto match(Val&& val, Ts... ts)
    {
        return std::visit(overloaded { ts... }, val);
    }

    using offset_t = uint32_t;

    template <typename E>
    constexpr typename std::underlying_type<E>::type to_underlying(E e) noexcept
    {
        return static_cast<typename std::underlying_type<E>::type>(e);
    }

    class FixedSizeBufferBackend
    {
    private:
        uint8_t* builder_buffer;
        offset_t current_size = 0;

    public:
        FixedSizeBufferBackend(const FixedSizeBufferBackend&) = delete;            // No copying allowed
        FixedSizeBufferBackend& operator=(const FixedSizeBufferBackend&) = delete; // No copy assignment
		FixedSizeBufferBackend(FixedSizeBufferBackend&& other)
			: builder_buffer(other.builder_buffer)
		{
			other.builder_buffer = nullptr;
		}

        FixedSizeBufferBackend(uint8_t* buffer)
        : builder_buffer(buffer)
        {
        }

        FixedSizeBufferBackend(offset_t max_size)
        : FixedSizeBufferBackend(new uint8_t[max_size] { 0 })
        {
        }

        ~FixedSizeBufferBackend()
        {
            delete[] builder_buffer;
        }

        std::pair<offset_t, uint8_t*> add_buffer(offset_t size)
        {
            auto buffer = builder_buffer + current_size;
            auto offset = current_size;
            current_size += size;

            return { offset, buffer };
        }

        uint8_t* get_new_buffer(offset_t size)
        {
            auto buffer = builder_buffer + current_size;
            current_size += size;
            return buffer;
        }

        offset_t add_string(const char* value, size_t len)
        {
            offset_t size   = static_cast<offset_t>(len + 1);
            uint8_t* buffer = builder_buffer + current_size;

            memcpy(buffer, value, len);
            buffer[size] = 0;

            auto offset = current_size;
            current_size += size;
            return offset;
        }

        offset_t get_size()
        {
            return current_size;
        }

        void clear()
        {
            memset(builder_buffer, 0, current_size);
            current_size = 0;
        }

        std::pair<offset_t, uint8_t*> build()
        {
            return { current_size, builder_buffer };
        }

        std::vector<uint8_t> build_vec()
        {
            return std::vector<uint8_t>(builder_buffer, builder_buffer + current_size);
        }
    };

    struct BufferTracker
    {
        uint8_t* buffer;
        offset_t size;
        offset_t free;

        inline offset_t used()
        {
            return size - free;
        }
    };

    class ExpandableBufferBackend
    {
    private:
        BufferTracker current_tracker;
        std::vector<BufferTracker> previous_trackers = {};
        offset_t current_size                        = 0;
        uint8_t* final_buffer                        = nullptr;

        const offset_t default_buffer_size;

    public:
        ExpandableBufferBackend(const ExpandableBufferBackend&) = delete;            // No copying allowed
        ExpandableBufferBackend& operator=(const ExpandableBufferBackend&) = delete; // No copy assignment
        ExpandableBufferBackend(ExpandableBufferBackend&& other)
            : current_tracker(std::move(other.current_tracker))
            , previous_trackers(std::move(other.previous_trackers))
            , current_size(other.current_size)
            , final_buffer(other.final_buffer)
            , default_buffer_size(other.default_buffer_size)
        {
            other.final_buffer = nullptr;
            other.current_tracker.buffer = nullptr;
            other.previous_trackers.clear();
        }

        ExpandableBufferBackend(offset_t default_buffer_size_ = 256)
        : default_buffer_size(default_buffer_size_)
        , current_tracker({ new uint8_t[default_buffer_size_] { 0 }, default_buffer_size_, default_buffer_size_ })
        {
        }

        ~ExpandableBufferBackend()
        {
            for (auto& buffer_tracker : previous_trackers)
            {
                delete[] buffer_tracker.buffer;
            }
            previous_trackers.clear();

            delete[] current_tracker.buffer;
            current_tracker.buffer = nullptr;
            delete final_buffer;
        }

        std::pair<offset_t, uint8_t*> add_buffer(offset_t size)
        {
            ensure_capacity(size);

            uint8_t* buffer = current_tracker.buffer + current_tracker.used();
            current_tracker.free -= size;

            auto offset = current_size;
            current_size += size;

            return { offset, buffer };
        }

        uint8_t* get_new_buffer(offset_t size)
        {
            ensure_capacity(size);

            uint8_t* buffer = current_tracker.buffer + current_tracker.used();
            current_tracker.free -= size;

            current_size += size;
            return buffer;
        }

        offset_t add_string(const char* value, size_t len)
        {
            offset_t size = static_cast<offset_t>(len + 1);

            ensure_capacity(size);

            uint8_t* buffer = current_tracker.buffer + current_tracker.used();
            current_tracker.free -= size;

            memcpy(buffer, value, len);

            auto offset = current_size;
            current_size += size;
            return offset;
        }

        offset_t get_size()
        {
            return current_size;
        }

        void ensure_capacity(size_t size)
        {
            if (current_tracker.free >= size)
            {
                return;
            }

            offset_t size_to_use = static_cast<offset_t>(size > default_buffer_size ? size : default_buffer_size);

            previous_trackers.push_back(current_tracker);
            current_tracker = {
                new uint8_t[size_to_use] { 0 },
                size_to_use,
                size_to_use
            };
        }

        void clear()
        {
            delete[] final_buffer;
            final_buffer = nullptr;

            delete[] current_tracker.buffer;
            current_tracker = { new uint8_t[default_buffer_size] { 0 }, default_buffer_size, default_buffer_size };

            for (auto& buffer_tracker : previous_trackers)
            {
                delete[] buffer_tracker.buffer;
            }
            previous_trackers.clear();

            current_size = 0;
        }

        std::pair<offset_t, uint8_t*> build()
        {
            if (previous_trackers.size() == 0)
            {
                return { current_size, current_tracker.buffer };
            }

            delete final_buffer;
            final_buffer = new uint8_t[current_size];
            auto offset  = 0;
            for (auto& buffer_tracker : previous_trackers)
            {
                memcpy(final_buffer + offset, buffer_tracker.buffer, buffer_tracker.used());
                offset += buffer_tracker.used();
            }
            memcpy(final_buffer + offset, current_tracker.buffer, current_tracker.used());
            offset += current_tracker.used();

            return { current_size, final_buffer };
        }

        std::vector<uint8_t> build_vec()
        {
            if (previous_trackers.size() == 0)
            {
                return std::vector<uint8_t>(current_tracker.buffer, current_tracker.buffer + current_size);
            }

            std::vector<uint8_t> out;
            out.resize(current_size);
            auto offset = 0;
            for (auto& buffer_tracker : previous_trackers)
            {
                memcpy(out.data() + offset, buffer_tracker.buffer, buffer_tracker.used());
                offset += buffer_tracker.used();
            }
            memcpy(out.data() + offset, current_tracker.buffer, current_tracker.used());

            return out;
        }
    };

    template <class BufferBackend>
    class BufferWriterBase
    {
    protected:
        BufferBackend& __backend;
        uint8_t* __buffer;
        const offset_t __self_offset;

        BufferWriterBase(BufferBackend& backend, uint8_t* buffer, offset_t self_offset)
        : __backend(backend)
        , __buffer(buffer)
        , __self_offset(self_offset)
        {
        }
    };

    template <typename T, typename BufferType>
    class PrimitiveContainer
    {
    private:
        BufferType __buffer;

    public:
        inline PrimitiveContainer(BufferType buffer)
        : __buffer(buffer)
        {
        }

        template <typename Backend>
        inline PrimitiveContainer(Backend&, uint8_t* buffer, offset_t)
        : __buffer(buffer)
        {
        }

        inline operator T() const
        {
            return value();
        }

        inline T value() const
        {
            T value;
            std::memcpy(&value, __buffer, sizeof(T));
            return value;
        }

        template <typename U = BufferType>
        inline typename std::enable_if<!std::is_const<U>::value, PrimitiveContainer&>::type operator=(const T& value)
        {
            set(value);
            return *this;
        }

        template <typename U = BufferType>
        inline typename std::enable_if<!std::is_const<U>::value, void>::type set(const T& value)
        {
            std::memcpy(__buffer, &value, sizeof(T));
        }

        constexpr static offset_t blitz_size()
        {
            return sizeof(T);
        }

        inline static bool check(const uint8_t* buffer, const offset_t length)
        {
            return length >= sizeof(T);
        }

        template <typename T2>
        friend std::ostream& operator<<(std::ostream& os, const PrimitiveContainer<T2, const uint8_t*>& container);
    };

    template <typename T>
    std::ostream& operator<<(std::ostream& os, const PrimitiveContainer<T, const uint8_t*>& container)
    {
        if constexpr (std::is_same_v<T, char>)
        {
            os << (int)(container.value());
        }
        else
        {
            os << container.value();
        }
        return os;
    }

    template <typename T>
    struct remove_primitive_container
    {
        using type = T;
    };

    template <typename T, typename U>
    struct remove_primitive_container<PrimitiveContainer<T, U>>
    {
        using type = T;
    };

    template <class T>
    using remove_primitive_container_t = typename remove_primitive_container<T>::type;

    template <typename T, typename BufferType>
    inline constexpr PrimitiveContainer<T, BufferType> make_primitive(BufferType buffer, offset_t offset)
    {
        return PrimitiveContainer<T, BufferType>(buffer + offset);
    }

    inline static bool check_string(const uint8_t* buffer, const offset_t length)
    {
        if (length < sizeof(offset_t))
        {
            return false;
        }

        offset_t offset = PrimitiveContainer<offset_t, const uint8_t*>(buffer);
        if (offset == 0)
        {
            return true;
        }
        if (offset >= length)
        {
            return false;
        }

        do
        {
            if (buffer[offset] == '\0')
            {
                return true;
            }
            offset++;
        } while (offset < length);

        return false;
    }

    template <typename T>
    inline static bool check_vector(const uint8_t* buffer, const offset_t length)
    {
        if (length < sizeof(offset_t))
        {
            return false;
        }

        offset_t offset = PrimitiveContainer<offset_t, const uint8_t*>(buffer);
        if (offset == 0)
        {
            return true;
        }
        if (offset >= length)
        {
            return false;
        }

        const offset_t vector_length = PrimitiveContainer<offset_t, const uint8_t*>(buffer + offset);
        offset += sizeof(offset_t);

        constexpr offset_t entry_size = T::blitz_size();
        const offset_t end_of_vector  = offset + vector_length * entry_size;
        if (end_of_vector > length)
        {
            return false;
        }

        while (offset < end_of_vector)
        {
            T::check(buffer + offset, length - offset);
            offset += entry_size;
        }

        return true;
    }

    template <typename T>
    class StringPointer
    {
    private:
        const uint8_t* __buffer;
        PrimitiveContainer<offset_t, const uint8_t*> __offset;

    public:
        inline StringPointer(const uint8_t* buffer)
        : __buffer(buffer)
        , __offset(buffer)
        {
        }

        inline operator T() const
        {
            return value();
        }

        inline T value() const
        {
            return (T)(__buffer + static_cast<offset_t>(__offset));
        }

        constexpr static offset_t blitz_size()
        {
            return sizeof(offset_t);
        }

        inline static bool check(const uint8_t* buffer, const offset_t length)
        {
            return check_string(buffer, length);
        }

        friend bool operator==(const StringPointer<const char*>& lhs, const StringPointer<const char*>& rhs);

        friend std::ostream& operator<<(std::ostream& os, const StringPointer<const char*>& ptr)
        {
            os << "\"" << ptr.value() << "\"";
            return os;
        }
    };

    inline bool operator==(const StringPointer<const char*>& lhs, const StringPointer<const char*>& rhs)
    {
        return strcmp(lhs.value(), rhs.value()) == 0;
    }

    template <class BufferBackend>
    class StringWriter
    {
    private:
        BufferBackend& __backend;
        uint8_t* __buffer;
        PrimitiveContainer<offset_t, uint8_t*> __offset;
        const offset_t __self_offset;

    public:
        StringWriter(BufferBackend& backend, uint8_t* buffer, offset_t self_offset)
        : __backend(backend)
        , __buffer(buffer)
        , __offset(buffer)
        , __self_offset(self_offset)
        {
        }

        constexpr static offset_t blitz_size()
        {
            return sizeof(offset_t);
        }

#ifdef __cpp_lib_string_view
        void insert_string(std::string_view value)
        {
            this->__offset = this->__backend.add_string(value.data(), value.length()) - this->__self_offset;
        }

        StringWriter& operator=(std::string_view value)
        {
            this->insert_string(value);
            return *this;
        }
#else
        void insert_string(const char* value)
        {
            this->__offset = this->__backend.add_string(value, strlen(value)) - this->__self_offset;
        }

        StringWriter& operator=(const char* value)
        {
            this->insert_string(value);
            return *this;
        }

        StringWriter& operator=(std::string value)
        {
            this->insert_string(value.c_str());
            return *this;
        }
#endif
    };

    template <class T, class BufferBackend>
    class VectorWriter
    {
    private:
        BufferBackend& __backend;
        uint8_t* __buffer;
        const offset_t __start_offset;
        const offset_t __element_size;

    public:
        VectorWriter(BufferBackend& backend, uint8_t* buffer, offset_t start_offset)
        : __backend(backend)
        , __buffer(buffer)
        , __start_offset(start_offset)
        , __element_size(T::blitz_size())
        {
        }

        static VectorWriter make_and_set_offset(BufferBackend& backend, offset_t length, offset_t buffer_offset, PrimitiveContainer<offset_t, uint8_t*> out_offset)
        {
            auto [offset, buffer] = backend.add_buffer(sizeof(offset_t) + T::blitz_size() * length);

            PrimitiveContainer<offset_t, uint8_t*> _length = { buffer };
            _length                                        = length;

            out_offset = offset - buffer_offset;
            return VectorWriter<T, BufferBackend>(backend, buffer + sizeof(offset_t), offset + sizeof(offset_t));
        }

        T operator[](int index)
        {
            auto element_offset = __element_size * index;
            return T(__backend, __buffer + element_offset, __start_offset + element_offset);
        }
    };
    template <class T, class BufferBackend>
    class VectorWriterPointer
    {
    private:
        BufferBackend& __backend;
        PrimitiveContainer<offset_t, uint8_t*> __offset;
        const offset_t __self_offset;

    public:
        VectorWriterPointer(BufferBackend& backend, PrimitiveContainer<offset_t, uint8_t*> offset, offset_t self_offset)
        : __backend(backend)
        , __offset(offset)
        , __self_offset(self_offset)
        {
        }

        constexpr static offset_t blitz_size()
        {
            return sizeof(offset_t);
        }

#ifdef __cpp_lib_span
        template <typename U>
        void insert(std::span<U> _raw_span)
        {
            auto length = static_cast<offset_t>(_raw_span.size());
            auto writer = VectorWriter<T, BufferBackend>::make_and_set_offset(this->__backend, length, this->__self_offset, this->__offset);
            for (offset_t i = 0; i < length; i++)
            {
                writer[i] = _raw_span[i];
            }
        }
#endif // __cpp_lib_span

        template <typename U>
        void insert(std::initializer_list<U> _raw_init)
        {
            auto length = static_cast<offset_t>(_raw_init.size());
            auto writer = VectorWriter<T, BufferBackend>::make_and_set_offset(this->__backend, length, this->__self_offset, this->__offset);
            auto iter   = _raw_init.begin();
            for (offset_t i = 0; i < length; i++)
            {
                writer[i] = *iter;
                iter++;
            }
        }

        template <typename U>
        void insert(const std::vector<U>& _raw_vec)
        {
            auto length = static_cast<offset_t>(_raw_vec.size());
            auto writer = VectorWriter<T, BufferBackend>::make_and_set_offset(this->__backend, length, this->__self_offset, this->__offset);
            for (offset_t i = 0; i < length; i++)
            {
                writer[i] = _raw_vec[i];
            }
        }

        template <typename U>
        void insert(const U* data, const offset_t data_length)
        {
            auto writer = VectorWriter<T, BufferBackend>::make_and_set_offset(this->__backend, data_length, this->__self_offset, this->__offset);
            for (offset_t i = 0; i < data_length; i++)
            {
                writer[i] = data[i];
            }
        }

        template <typename U>
        VectorWriterPointer<T, BufferBackend>& operator=(const std::vector<U>& _raw_vec)
        {
            this->insert(_raw_vec);
            return *this;
        }
    };
    template <typename T>
    class VectorIter
    {
    private:
        const uint8_t* buffer;
        const PrimitiveContainer<offset_t, const uint8_t*> len;
        const offset_t entry_size;
        offset_t index = 0;

    public:
        using iterator_category = std::forward_iterator_tag;
        using difference_type   = std::ptrdiff_t;
        using value_type        = T;
        using pointer           = T*;
        using reference         = T&;

        inline VectorIter(const uint8_t* _buffer, offset_t _entry_size, offset_t _start_index = 0)
        : len(_buffer)
        , buffer(_buffer + sizeof(offset_t))
        , entry_size(_entry_size)
        , index(_start_index)
        {
        }

        inline VectorIter<T> operator++()
        {
            index += entry_size;
            return *this;
        }

        inline T operator*()
        {
            return T(buffer + index);
        }

        friend bool operator==(const VectorIter<T>& a, const VectorIter<T>& b)
        {
            return a.buffer == b.buffer && a.index == b.index;
        }

        friend bool operator!=(const VectorIter<T>& a, const VectorIter<T>& b)
        {
            return a.buffer != b.buffer || a.index != b.index;
        }
    };

    template <typename T>
    class Vector
    {
    private:
        const uint8_t* buffer;

    public:
        inline Vector(const uint8_t* _buffer)
        : buffer(_buffer)
        {
        }

        inline constexpr static offset_t blitz_size()
        {
            return sizeof(offset_t);
        }

        inline offset_t offset() const
        {
            const PrimitiveContainer<offset_t, const uint8_t*> offset(buffer);
            return offset.value();
        }

        inline offset_t length() const
        {
            const PrimitiveContainer<offset_t, const uint8_t*> len(buffer + offset());
            return len.value();
        }

        inline const remove_primitive_container_t<T>* data_ptr() const
        {
            return static_cast<const remove_primitive_container_t<T>*>(buffer + offset() + sizeof(offset_t));
        }

        inline VectorIter<T> begin() const
        {
            return VectorIter<T>(buffer + offset(), T::blitz_size());
        }

        inline VectorIter<T> end() const
        {
            return VectorIter<T>(buffer + offset(), T::blitz_size(), length() * T::blitz_size());
        }

        inline T operator[](int index) const
        {
            return T(buffer + offset() + sizeof(offset_t) + index * T::blitz_size());
        }

        inline static bool check(const uint8_t* buffer, const offset_t length)
        {
            return check_vector<T>(buffer, length);
        }

        template <typename T2>
        friend bool operator==(const Vector<T2>& lhs, const Vector<T2>& rhs);

        template <typename T2>
        friend std::ostream& operator<<(std::ostream& os, const Vector<T2>& vector);
    };

    template <typename T>
    inline bool operator==(const Vector<T>& lhs, const Vector<T>& rhs)
    {
        if (lhs.length() != rhs.length())
        {
            return false;
        }
        for (offset_t i = 0; i < lhs.length(); i++)
        {
            if (lhs[i] != rhs[i])
            {
                return false;
            }
        }
        return true;
    }

    template <typename T>
    inline std::ostream& operator<<(std::ostream& os, const Vector<T>& vector)
    {
        os << "Vector[";
        if (vector.length() > 0)
        {
            os << vector[0];
            for (offset_t i = 1; i < vector.length(); i++)
            {
                if constexpr (std::is_same_v<T, char>)
                {
                    os << ", " << (int)(vector[i]);
                }
                else
                {
                    os << ", " << vector[i];
                }
            }
        }
        os << "]";
        return os;
    }
}
