pub mod blitzbuffers {
    use std::{
        borrow::Borrow, cell::UnsafeCell, cmp::max, convert::TryInto, iter::Zip,
        marker::PhantomData, ops::Index,
    };

    // region: Standard types setup

    pub trait PrimitiveByteFunctions: Sized + PartialEq + std::fmt::Debug {
        unsafe fn write_le_bytes(&self, bytes: &mut [u8]);
        unsafe fn read_le_bytes(bytes: &[u8]) -> Self;
    }

    macro_rules! impl_traits_for_primitive {
        ($byte_type:ty) => {
            impl PrimitiveByteFunctions for $byte_type {
                #[inline(always)]
                unsafe fn write_le_bytes(&self, bytes: &mut [u8]) {
                    bytes
                        .get_unchecked_mut(..size_of::<Self>())
                        .copy_from_slice(&self.to_le_bytes())
                }

                #[inline(always)]
                unsafe fn read_le_bytes(bytes: &[u8]) -> Self {
                    Self::from_le_bytes(bytes[..size_of::<Self>()].try_into().unwrap())
                }
            }

            impl BlitzSized for $byte_type {
                #[inline(always)]
                fn get_blitz_size() -> u32 {
                    size_of::<Self>() as u32
                }
            }

            impl BlitzCalcSize for $byte_type {
                #[inline(always)]
                fn calc_blitz_size(&self) -> u32 {
                    size_of::<Self>() as u32
                }
            }

            impl BlitzCheck for $byte_type {
                #[inline(always)]
                fn blitz_check(buffer: &[u8]) -> Result<(), String> {
                    Ok(())
                }
            }

            impl BlitzViewer<'_> for $byte_type {
                #[inline(always)]
                fn new_blitz_view(buffer: &[u8]) -> Self {
                    unsafe { <$byte_type>::read_le_bytes(buffer) }
                }
            }
        };
    }

    impl_traits_for_primitive!(u8);
    impl_traits_for_primitive!(u16);
    impl_traits_for_primitive!(u32);
    impl_traits_for_primitive!(u64);
    impl_traits_for_primitive!(u128);

    impl_traits_for_primitive!(i8);
    impl_traits_for_primitive!(i16);
    impl_traits_for_primitive!(i32);
    impl_traits_for_primitive!(i64);
    impl_traits_for_primitive!(i128);

    impl_traits_for_primitive!(f32);
    impl_traits_for_primitive!(f64);

    impl PrimitiveByteFunctions for bool {
        #[inline(always)]
        unsafe fn write_le_bytes(&self, bytes: &mut [u8]) {
            bytes
                .get_unchecked_mut(..size_of::<u8>())
                .copy_from_slice(&(if *self { 1u8 } else { 0u8 }).to_le_bytes())
        }

        #[inline(always)]
        unsafe fn read_le_bytes(bytes: &[u8]) -> Self {
            u8::from_le_bytes(bytes[..size_of::<u8>()].try_into().unwrap()) > 0
        }
    }

    impl BlitzSized for bool {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            1
        }
    }

    impl BlitzCalcSize for bool {
        #[inline(always)]
        fn calc_blitz_size(&self) -> u32 {
            1
        }
    }

    impl<'a> BlitzViewer<'a> for bool {
        #[inline(always)]
        fn new_blitz_view(buffer: &'a [u8]) -> Self {
            unsafe { u8::read_le_bytes(buffer) > 0 }
        }
    }

    impl BlitzCheck for bool {
        #[inline(always)]
        fn blitz_check(buffer: &[u8]) -> Result<(), String> {
            Ok(())
        }
    }

    impl<T: BlitzCalcSize> BlitzCalcSize for Vec<T> {
        #[inline(always)]
        fn calc_blitz_size(&self) -> u32 {
            if self.len() > 0 {
                let element_size: u32 = self.iter().map(|inner| inner.calc_blitz_size()).sum();
                element_size + size_of::<u32>() as u32 + size_of::<u32>() as u32
            } else {
                size_of::<u32>() as u32
            }
        }
    }

    impl BlitzSized for &str {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl BlitzCalcSize for &str {
        #[inline(always)]
        fn calc_blitz_size(&self) -> u32 {
            if self.len() > 0 {
                (self.len() + size_of::<u32>()) as u32 + 1 // Offset and null-termination
            } else {
                size_of::<u32>() as u32 // Offset
            }
        }
    }

    impl BlitzSized for String {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl BlitzCalcSize for String {
        #[inline(always)]
        fn calc_blitz_size(&self) -> u32 {
            if self.len() > 0 {
                (self.len() + size_of::<u32>()) as u32 + 1 // Offset and null-termination
            } else {
                size_of::<u32>() as u32 // Offset
            }
        }
    }

    impl<'a> BlitzViewer<'a> for &str {
        #[inline(always)]
        fn new_blitz_view(buffer: &'a [u8]) -> Self {
            let offset = unsafe { u32::read_le_bytes(buffer) };
            unsafe {
                std::ffi::CStr::from_ptr(buffer.as_ptr().add(offset as usize) as *const i8)
                    .to_str()
                    .unwrap()
            }
        }
    }

    #[inline(always)]
    fn check_string(buffer: &[u8]) -> Result<(), String> {
        if buffer.len() < 4 {
            return Err("Buffer too short to hold string offset.".to_string());
        }
        let mut offset = unsafe { u32::read_le_bytes(buffer) } as usize;
        if offset == 0 {
            return Ok(());
        }
        if offset >= buffer.len() {
            return Err("String offset is outside of the buffer.".to_string());
        }
        loop {
            if buffer[offset] == b'\0' {
                return Ok(());
            }
            offset += 1;
            if offset >= buffer.len() {
                return Err("Buffer too short to contain the string.".to_string());
            }
        }
    }

    impl BlitzCheck for String {
        #[inline(always)]
        fn blitz_check(buffer: &[u8]) -> Result<(), String> {
            check_string(buffer)
        }
    }

    impl BlitzCheck for &str {
        #[inline(always)]
        fn blitz_check(buffer: &[u8]) -> Result<(), String> {
            check_string(buffer)
        }
    }

    // endregion: Standard types setup

    // region: Backend

    pub trait BlitzBufferBackend: Sized {
        fn add_buffer(&mut self, buffer: Vec<u8>) -> u32;
        fn get_new_buffer(&mut self, size: u32) -> &mut [u8];
        fn add_string(&mut self, str: impl AsRef<str>) -> u32;
        fn add_string_bytes(&mut self, bytes: &[u8]) -> u32;
        fn get_size(&self) -> u32;
        fn clear(&mut self);
        fn build(&self) -> Vec<u8>;
        fn into_buffer(self) -> Vec<u8>;
    }

    pub struct FixedSizeBufferBackend<const N: usize> {
        buffer: [u8; N],
        current_size: u32,
    }

    impl<const N: usize> FixedSizeBufferBackend<N> {
        #[inline(always)]
        pub fn new() -> UnsafeBlitzBufferBackend<Self> {
            UnsafeBlitzBufferBackend {
                backend: Self {
                    buffer: [0u8; N],
                    current_size: 0,
                }
                .into(),
            }
        }
    }

    impl<const N: usize> BlitzBufferBackend for FixedSizeBufferBackend<N> {
        #[inline(always)]
        fn add_buffer(&mut self, buffer: Vec<u8>) -> u32 {
            let offset = self.current_size;

            let start = self.current_size as usize;
            self.current_size += buffer.len() as u32;
            let end = self.current_size as usize;
            unsafe {
                self.buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(&buffer)
            };
            return offset;
        }

        #[inline(always)]
        fn get_new_buffer(&mut self, size: u32) -> &mut [u8] {
            let ptr = self.buffer.as_mut_ptr();
            let buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    ptr.add(self.current_size as usize),
                    size as usize,
                )
            };
            self.current_size += size;
            return buffer;
        }

        #[inline(always)]
        fn add_string(&mut self, str: impl AsRef<str>) -> u32 {
            return self.add_string_bytes(str.as_ref().as_bytes());
        }

        #[inline(always)]
        fn add_string_bytes(&mut self, bytes: &[u8]) -> u32 {
            let offset = self.current_size;

            let start = self.current_size as usize;
            self.current_size += bytes.len() as u32;
            let end = self.current_size as usize;
            unsafe {
                self.buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(bytes)
            };

            self.buffer[end] = 0;
            self.current_size += 1;
            return offset;
        }

        #[inline(always)]
        fn get_size(&self) -> u32 {
            self.current_size
        }

        #[inline(always)]
        fn clear(&mut self) {
            self.current_size = 0;
        }

        #[inline(always)]
        fn build(&self) -> Vec<u8> {
            unsafe { self.buffer.get_unchecked(..self.current_size as usize) }.to_vec()
        }

        #[inline(always)]
        fn into_buffer(self) -> Vec<u8> {
            self.buffer.to_vec()
        }
    }

    struct BufferTracker {
        buffer: Vec<u8>,
        free: u32,
    }

    impl BufferTracker {
        #[inline(always)]
        pub fn used(&self) -> usize {
            self.buffer.len() - self.free as usize
        }
    }

    pub struct ExpandableBufferBackend {
        current_tracker: BufferTracker,
        prev_trackers: Vec<BufferTracker>,
        current_size: u32,
        default_size: u32,
    }

    impl ExpandableBufferBackend {
        const DEFAULT_BUFFER_SIZE: u32 = 256;

        #[inline(always)]
        pub fn new(size: u32) -> UnsafeBlitzBufferBackend<Self> {
            UnsafeBlitzBufferBackend {
                backend: Self {
                    current_tracker: BufferTracker {
                        buffer: vec![0u8; size as usize],
                        free: size,
                    },
                    prev_trackers: Default::default(),
                    current_size: 0,
                    default_size: size,
                }
                .into(),
            }
        }

        #[inline(always)]
        pub fn new_with_default_size() -> UnsafeBlitzBufferBackend<Self> {
            Self::new(Self::DEFAULT_BUFFER_SIZE)
        }

        #[inline(always)]
        fn ensure_capacity(&mut self, size: u32) {
            if self.current_tracker.free >= size {
                return;
            }

            let new_size = max(size, self.default_size);
            self.prev_trackers.push(std::mem::replace(
                &mut self.current_tracker,
                BufferTracker {
                    buffer: vec![0u8; new_size as usize],
                    free: new_size,
                },
            ));
        }
    }

    impl BlitzBufferBackend for ExpandableBufferBackend {
        #[inline(always)]
        fn add_buffer(&mut self, buffer: Vec<u8>) -> u32 {
            let size = buffer.len() as u32;
            self.ensure_capacity(size);

            let offset = self.current_size;
            self.current_size += size;

            unsafe {
                let start = self.current_tracker.used();
                let end = start + size as usize;
                self.current_tracker
                    .buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(&buffer);
            }
            self.current_tracker.free -= size;

            return offset;
        }

        #[inline(always)]
        fn get_new_buffer(&mut self, size: u32) -> &mut [u8] {
            self.ensure_capacity(size);
            self.current_size += size;

            let buffer = unsafe {
                let ptr = self
                    .current_tracker
                    .buffer
                    .as_mut_ptr()
                    .add(self.current_tracker.used());

                &mut *std::ptr::slice_from_raw_parts_mut(ptr, size as usize)
            };
            self.current_tracker.free -= size;

            return buffer;
        }

        #[inline(always)]
        fn add_string(&mut self, str: impl AsRef<str>) -> u32 {
            return self.add_string_bytes(str.as_ref().as_bytes());
        }

        #[inline(always)]
        fn add_string_bytes(&mut self, bytes: &[u8]) -> u32 {
            // Add 1 to make space for zero-byte at end of string
            let size = bytes.len() as u32 + 1;
            self.ensure_capacity(size);

            let offset = self.current_size;
            self.current_size += size;

            unsafe {
                let start = self.current_tracker.used();
                let end = start + size as usize - 1;

                self.current_tracker
                    .buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(bytes);
                self.current_tracker.buffer[end] = 0x00; // Zero byte to end string
            }
            self.current_tracker.free -= size;

            return offset;
        }

        #[inline(always)]
        fn get_size(&self) -> u32 {
            self.current_size
        }

        #[inline(always)]
        fn clear(&mut self) {
            self.current_tracker = BufferTracker {
                buffer: vec![0u8; self.default_size as usize],
                free: self.default_size,
            };
            self.prev_trackers.clear();
            self.current_size = 0;
        }

        #[inline(always)]
        fn build(&self) -> Vec<u8> {
            if self.prev_trackers.is_empty() {
                return (&self.current_tracker.buffer[..self.current_tracker.used()]).to_vec();
            }

            self.prev_trackers
                .iter()
                .map(|tracker| &tracker.buffer[..tracker.used()])
                .chain(std::iter::once(
                    &self.current_tracker.buffer[..self.current_tracker.used()],
                ))
                .flatten()
                .copied()
                .collect()
        }

        #[inline(always)]
        fn into_buffer(self) -> Vec<u8> {
            if self.prev_trackers.is_empty() {
                return self.current_tracker.buffer[..self.current_tracker.used()].to_vec();
            }

            self.prev_trackers
                .iter()
                .map(|tracker| &tracker.buffer[..tracker.used()])
                .chain(std::iter::once(
                    &self.current_tracker.buffer[..self.current_tracker.used()],
                ))
                .flatten()
                .copied()
                .collect()
        }
    }

    // Only for use internally when the total size of the final data is known.
    pub(crate) struct UnsafeDirectBufferBackend {
        buffer: Vec<u8>,
        current_size: u32,
    }

    impl UnsafeDirectBufferBackend {
        #[inline(always)]
        pub(crate) unsafe fn new(size: usize) -> UnsafeBlitzBufferBackend<Self> {
            let mut buffer = Vec::with_capacity(size);
            buffer.set_len(size);
            UnsafeBlitzBufferBackend {
                backend: UnsafeDirectBufferBackend {
                    buffer,
                    current_size: 0,
                }
                .into(),
            }
        }
    }

    impl BlitzBufferBackend for UnsafeDirectBufferBackend {
        #[inline(always)]
        fn add_buffer(&mut self, buffer: Vec<u8>) -> u32 {
            let offset = self.current_size;

            let start = self.current_size as usize;
            self.current_size += buffer.len() as u32;
            let end = self.current_size as usize;
            unsafe {
                self.buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(&buffer)
            };
            return offset;
        }

        #[inline(always)]
        fn get_new_buffer(&mut self, size: u32) -> &mut [u8] {
            let ptr = self.buffer.as_mut_ptr();
            let buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    ptr.add(self.current_size as usize),
                    size as usize,
                )
            };
            self.current_size += size;
            return buffer;
        }

        #[inline(always)]
        fn add_string(&mut self, str: impl AsRef<str>) -> u32 {
            return self.add_string_bytes(str.as_ref().as_bytes());
        }

        #[inline(always)]
        fn add_string_bytes(&mut self, bytes: &[u8]) -> u32 {
            let offset = self.current_size;

            let start = self.current_size as usize;
            self.current_size += bytes.len() as u32;
            let end = self.current_size as usize;
            unsafe {
                self.buffer
                    .get_unchecked_mut(start..end)
                    .copy_from_slice(&bytes)
            };

            self.buffer[end] = 0;
            self.current_size += 1;
            return offset;
        }

        #[inline(always)]
        fn get_size(&self) -> u32 {
            self.current_size
        }

        #[inline(always)]
        fn clear(&mut self) {
            self.current_size = 0;
        }

        #[inline(always)]
        fn build(&self) -> Vec<u8> {
            unsafe { self.buffer.get_unchecked(..self.current_size as usize) }.to_vec()
        }

        #[inline(always)]
        fn into_buffer(self) -> Vec<u8> {
            self.buffer
        }
    }

    pub struct UnsafeBlitzBufferBackend<Backend> {
        backend: UnsafeCell<Backend>,
    }

    unsafe impl<Backend> Send for UnsafeBlitzBufferBackend<Backend> {}

    unsafe impl<Backend> Sync for UnsafeBlitzBufferBackend<Backend> {}

    impl<Backend> UnsafeBlitzBufferBackend<Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn get_mut_backend(&self) -> &mut Backend {
            unsafe { &mut (*self.backend.get()) }
        }

        #[inline(always)]
        pub fn add_buffer(&self, buffer: Vec<u8>) -> u32 {
            self.get_mut_backend().add_buffer(buffer)
        }

        #[inline(always)]
        pub fn get_new_buffer(&self, size: u32) -> &mut [u8] {
            self.get_mut_backend().get_new_buffer(size)
        }

        #[inline(always)]
        pub fn add_string(&self, str: impl AsRef<str>) -> u32 {
            self.get_mut_backend().add_string(str)
        }

        #[inline(always)]
        pub fn add_string_bytes(&self, bytes: &[u8]) -> u32 {
            self.get_mut_backend().add_string_bytes(bytes)
        }

        #[inline(always)]
        pub fn get_size(&self) -> u32 {
            self.get_mut_backend().get_size()
        }

        #[inline(always)]
        pub fn clear(&self) {
            self.get_mut_backend().clear()
        }

        #[inline(always)]
        pub fn build(&self) -> Vec<u8> {
            self.get_mut_backend().build()
        }

        #[inline(always)]
        pub fn into_buffer(self) -> Vec<u8> {
            self.backend.into_inner().into_buffer()
        }
    }

    // endregion: Backend

    // region: Traits

    pub trait BlitzSized: Sized {
        fn get_blitz_size() -> u32;
    }

    pub trait BlitzCalcSize {
        fn calc_blitz_size(&self) -> u32;
    }

    pub trait BlitzCheck {
        fn blitz_check(buffer: &[u8]) -> Result<(), String>;
    }

    pub trait BlitzCopyFrom<T> {
        fn copy_from(&mut self, value: T);
    }

    pub trait BlitzBuilder<'a, Backend> {
        fn new_blitz_builder(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            self_offset: u32,
        ) -> Self;
    }

    pub trait BlitzViewer<'a> {
        fn new_blitz_view(buffer: &'a [u8]) -> Self;
    }

    pub trait BlitzIndexSet<T> {
        fn set(&mut self, index: usize, value: T);
    }

    // endregion: Traits

    // region: BlitzPrimitiveWriter

    /// Writes a primitive T at the start of its buffer.
    pub struct BlitzPrimitiveWriter<'a, T> {
        buffer: &'a mut [u8],
        _pd: PhantomData<T>,
    }

    impl<T> BlitzSized for BlitzPrimitiveWriter<'_, T>
    where
        T: BlitzSized,
    {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            T::get_blitz_size()
        }
    }

    impl<'a, Backend, T> BlitzBuilder<'a, Backend> for BlitzPrimitiveWriter<'a, T>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn new_blitz_builder(
            _backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            _self_offset: u32,
        ) -> Self {
            Self {
                buffer,
                _pd: Default::default(),
            }
        }
    }

    impl<'a, T> BlitzPrimitiveWriter<'a, T>
    where
        T: PrimitiveByteFunctions,
    {
        #[inline(always)]
        pub fn set(&mut self, value: impl Borrow<T>) {
            unsafe {
                value.borrow().write_le_bytes(&mut self.buffer);
            }
        }
    }

    impl<'a, T> BlitzCopyFrom<&T> for BlitzPrimitiveWriter<'_, T>
    where
        T: PrimitiveByteFunctions,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: &T) {
            self.set(value);
        }
    }

    impl<'a, T> BlitzCopyFrom<T> for BlitzPrimitiveWriter<'_, T>
    where
        T: PrimitiveByteFunctions,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: T) {
            self.set(value);
        }
    }

    // endregion: BlitzPrimitiveWriter

    // region: BlitzStringWriter

    /// Writes a string to the backend and puts an offset at the start of the buffer.
    pub struct BlitzStringWriter<'a, Backend> {
        backend: &'a UnsafeBlitzBufferBackend<Backend>,
        buffer: &'a mut [u8],
        self_offset: u32,
    }

    impl<Backend> BlitzSized for BlitzStringWriter<'_, Backend> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<'a, Backend> BlitzBuilder<'a, Backend> for BlitzStringWriter<'a, Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn new_blitz_builder(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            self_offset: u32,
        ) -> Self {
            Self {
                backend,
                buffer,
                self_offset,
            }
        }
    }

    impl<Backend> BlitzStringWriter<'_, Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn set(&mut self, value: impl AsRef<str>) {
            if (value.as_ref().is_empty()) {
                return;
            }
            let offset = self.backend.add_string(value.as_ref()) - self.self_offset;
            unsafe {
                offset.write_le_bytes(&mut self.buffer);
            }
        }
    }

    impl<'a, Backend> BlitzCopyFrom<String> for BlitzStringWriter<'_, Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: String) {
            self.set(value);
        }
    }

    impl<'a, Backend> BlitzCopyFrom<&String> for BlitzStringWriter<'_, Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: &String) {
            self.set(value);
        }
    }

    impl<'a, Backend> BlitzCopyFrom<&str> for BlitzStringWriter<'_, Backend>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: &str) {
            self.set(value);
        }
    }

    // endregion: BlitzStringWriter

    // region: BlitzVectorWriterPointer

    pub struct BlitzVectorWriterPointer<'a, Backend, T> {
        backend: &'a UnsafeBlitzBufferBackend<Backend>,
        buffer: &'a mut [u8],
        self_offset: u32,
        _pd: PhantomData<T>,
    }

    impl<Backend, T> BlitzSized for BlitzVectorWriterPointer<'_, Backend, T> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<'a, Backend, T> BlitzBuilder<'a, Backend> for BlitzVectorWriterPointer<'a, Backend, T> {
        #[inline(always)]
        fn new_blitz_builder(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            self_offset: u32,
        ) -> Self {
            Self {
                backend,
                buffer,
                self_offset,
                _pd: PhantomData,
            }
        }
    }

    impl<'a, Backend, T, U, IterU> BlitzCopyFrom<IterU> for BlitzVectorWriterPointer<'a, Backend, T>
    where
        IterU: IntoIterator<Item = U>,
        IterU::IntoIter: ExactSizeIterator,
        T: BlitzBuilder<'a, Backend> + BlitzCopyFrom<U> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: IterU) {
            let iter = value.into_iter();
            if (iter.len() == 0) {
                return;
            }
            let mut content = self.alloc_vector(iter.len() as u32);
            iter.zip(content.iter_mut()).for_each(|(from, mut to)| {
                to.copy_from(from);
            });
        }
    }

    impl<'a, Backend, T> BlitzVectorWriterPointer<'a, Backend, T>
    where
        Backend: BlitzBufferBackend,
        T: BlitzSized,
    {
        #[inline(always)]
        pub(crate) fn new_at_offset(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &mut [u8],
            start_offset: u32,
            offset: u32,
        ) -> Self {
            let offset_buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    buffer.as_mut_ptr().add(offset as usize),
                    size_of::<u32>(),
                )
            };
            Self {
                backend,
                buffer: offset_buffer,
                self_offset: start_offset + offset,
                _pd: Default::default(),
            }
        }

        #[inline(always)]
        pub fn alloc_vector(&mut self, length: u32) -> BlitzVectorWriter<'a, Backend, T> {
            let writer = BlitzVectorWriter::new(self.backend, length);
            let offset = writer.self_offset - self.self_offset;
            unsafe {
                self.buffer
                    .get_unchecked_mut(0..4)
                    .copy_from_slice(&offset.to_le_bytes());
            }
            writer
        }
    }

    // endregion: BlitzVectorWriterPointer

    // region: BlitzVectorWriter

    pub struct BlitzVectorWriter<'a, Backend, T> {
        backend: &'a UnsafeBlitzBufferBackend<Backend>,
        buffer: &'a mut [u8],
        self_offset: u32,
        _pd: PhantomData<T>,
    }

    impl<Backend, T> BlitzSized for BlitzVectorWriter<'_, Backend, T> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<'a, Backend, T> BlitzVectorWriter<'a, Backend, T>
    where
        T: BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn new(backend: &'a UnsafeBlitzBufferBackend<Backend>, len: u32) -> Self {
            let self_offset = backend.get_size();
            let buffer =
                backend.get_new_buffer(size_of::<u32>() as u32 + len * T::get_blitz_size());
            // Set size of vector
            unsafe {
                buffer
                    .get_unchecked_mut(0..4)
                    .copy_from_slice(&len.to_le_bytes());
            }
            Self {
                backend,
                buffer,
                self_offset,
                _pd: Default::default(),
            }
        }

        #[inline(always)]
        pub fn len(&self) -> u32 {
            unsafe { u32::read_le_bytes(self.buffer.get_unchecked(0..4)) }
        }
    }

    impl<'a, Backend, T> BlitzVectorWriter<'a, Backend, T>
    where
        T: BlitzBuilder<'a, Backend> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn get_mut(&mut self, index: usize) -> T {
            let offset = size_of::<u32>() + (T::get_blitz_size() as usize) * index;
            let buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    self.buffer.as_mut_ptr().add(offset),
                    T::get_blitz_size() as usize,
                )
            };

            T::new_blitz_builder(&self.backend, buffer, self.self_offset + offset as u32)
        }
    }

    impl<'a, Backend, T> BlitzVectorWriter<'a, Backend, T>
    where
        T: BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn iter_mut(&mut self) -> BlitzIterWriter<'a, Backend, T> {
            let buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    self.buffer.as_mut_ptr(),
                    self.buffer.len(),
                )
            };
            BlitzIterWriter::new_blitz_builder(&self.backend, buffer, self.self_offset)
        }
    }

    impl<Backend, T> BlitzVectorWriter<'_, Backend, BlitzVectorWriter<'_, Backend, T>>
    where
        T: BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn insert_vector(
            &mut self,
            index: usize,
            len: u32,
        ) -> BlitzVectorWriter<'_, Backend, T> {
            let start = size_of::<u32>() + index * size_of::<u32>();
            let offset = self.backend.get_size() - self.self_offset - start as u32;
            unsafe {
                offset.write_le_bytes(self.buffer.get_unchecked_mut(start..));
            };
            BlitzVectorWriter::new(&self.backend, len)
        }
    }

    impl<'a, Backend, T, U> BlitzCopyFrom<&[U]> for BlitzVectorWriter<'a, Backend, T>
    where
        U: Clone,
        T: BlitzBuilder<'a, Backend> + BlitzCopyFrom<U> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: &[U]) {
            if (value.is_empty()) {
                return;
            }
            value
                .iter()
                .zip(self.iter_mut())
                .for_each(|(from, mut to)| to.copy_from(from.clone()));
        }
    }

    impl<'a, Backend, T, U> BlitzCopyFrom<Vec<U>> for BlitzVectorWriter<'a, Backend, T>
    where
        T: BlitzBuilder<'a, Backend> + BlitzCopyFrom<U> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, value: Vec<U>) {
            if (value.is_empty()) {
                return;
            }
            value
                .into_iter()
                .zip(self.iter_mut())
                .for_each(|(from, mut to)| to.copy_from(from));
        }
    }

    impl<'a, Backend, T> BlitzIndexSet<T> for BlitzVectorWriter<'a, Backend, T>
    where
        T: PrimitiveByteFunctions,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn set(&mut self, index: usize, value: T) {
            let start = size_of::<u32>() + index * size_of::<T>();
            unsafe {
                value.write_le_bytes(self.buffer.get_unchecked_mut(start..));
            }
        }
    }

    impl<Backend> BlitzIndexSet<&str> for BlitzVectorWriter<'_, Backend, &str>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn set(&mut self, index: usize, value: &str) {
            let offset = self.backend.add_string(value);
            let start = size_of::<u32>() + index * size_of::<u32>();
            unsafe {
                offset.write_le_bytes(self.buffer.get_unchecked_mut(start..));
            }
        }
    }

    impl<Backend> BlitzIndexSet<String> for BlitzVectorWriter<'_, Backend, String>
    where
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn set(&mut self, index: usize, value: String) {
            let start = size_of::<u32>() + index * size_of::<u32>();
            let offset = self.backend.add_string(value) - self.self_offset - start as u32;
            unsafe {
                offset.write_le_bytes(self.buffer.get_unchecked_mut(start..));
            }
        }
    }

    // endregion: BlitzVectorWriter

    // region: BlitzIterWriterPointer

    pub struct BlitzIterWriterPointer<'a, Backend, T> {
        backend: &'a UnsafeBlitzBufferBackend<Backend>,
        buffer: &'a mut [u8],
        self_offset: u32,
        _pd: PhantomData<T>,
    }

    impl<'a, Backend, T> BlitzBuilder<'a, Backend> for BlitzIterWriterPointer<'a, Backend, T> {
        #[inline(always)]
        fn new_blitz_builder(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            self_offset: u32,
        ) -> Self {
            Self {
                backend,
                buffer,
                self_offset,
                _pd: Default::default(),
            }
        }
    }

    impl<'a, Backend, T> BlitzSized for BlitzIterWriterPointer<'a, Backend, T> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<'a, Backend, T, IterT, U, IterU> BlitzCopyFrom<IterU>
        for BlitzIterWriterPointer<'a, Backend, IterT>
    where
        IterT: Iterator<Item = T>,
        IterU: Iterator<Item = U> + ExactSizeIterator,
        T: BlitzBuilder<'a, Backend> + BlitzCopyFrom<U> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, iter: IterU) {
            if (iter.len() == 0) {
                return;
            }

            let iter_writer = BlitzIterWriter::<'a, Backend, T>::alloc_with_len(
                self.backend,
                &mut self.buffer,
                self.self_offset,
                iter.len() as u32,
            );

            iter.zip(iter_writer).for_each(|(from, mut to)| {
                to.copy_from(from);
            });
        }
    }

    // endregion: BlitzIterWriterPointer

    // region: BlitzIterWriter

    pub struct BlitzIterWriter<'a, Backend, T> {
        backend: &'a UnsafeBlitzBufferBackend<Backend>,
        buffer: &'a mut [u8],
        self_offset: u32,
        len: u32,
        index: u32,
        _pd: PhantomData<T>,
    }

    impl<Backend, T> BlitzSized for BlitzIterWriter<'_, Backend, T> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<'a, Backend, T> BlitzBuilder<'a, Backend> for BlitzIterWriter<'a, Backend, T> {
        #[inline(always)]
        fn new_blitz_builder(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            buffer: &'a mut [u8],
            self_offset: u32,
        ) -> Self {
            let len = unsafe { u32::read_le_bytes(buffer.get_unchecked(0..4)) };
            Self {
                backend,
                buffer,
                self_offset,
                len,
                index: 0,
                _pd: Default::default(),
            }
        }
    }

    impl<'a, Backend, T> BlitzIterWriter<'a, Backend, T>
    where
        T: BlitzSized,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        pub fn alloc_with_len(
            backend: &'a UnsafeBlitzBufferBackend<Backend>,
            pointer_buffer: &mut [u8],
            pointer_offset: u32,
            len: u32,
        ) -> Self {
            let offset = backend.get_size() - pointer_offset;
            // Set offset of iterable
            unsafe {
                pointer_buffer
                    .get_unchecked_mut(0..4)
                    .copy_from_slice(&offset.to_le_bytes());
            }

            let self_offset = backend.get_size();
            let buffer =
                backend.get_new_buffer(size_of::<u32>() as u32 + len * T::get_blitz_size());
            // Set size of vector
            unsafe {
                buffer
                    .get_unchecked_mut(0..4)
                    .copy_from_slice(&len.to_le_bytes());
            }
            Self {
                backend,
                buffer,
                self_offset,
                len,
                index: 0,
                _pd: Default::default(),
            }
        }
    }

    impl<'a, Backend, T, U, IterU> BlitzCopyFrom<IterU> for BlitzIterWriter<'a, Backend, T>
    where
        T: BlitzBuilder<'a, Backend> + BlitzCopyFrom<U> + BlitzSized,
        IterU: Iterator<Item = U>,
        Backend: BlitzBufferBackend,
    {
        #[inline(always)]
        fn copy_from(&mut self, iter: IterU) {
            iter.zip(self).for_each(|(from, mut to)| {
                to.copy_from(from);
            });
        }
    }

    impl<'a, Backend, T> Iterator for BlitzIterWriter<'a, Backend, T>
    where
        T: BlitzBuilder<'a, Backend> + BlitzSized,
        Backend: BlitzBufferBackend,
    {
        type Item = T;

        #[inline(always)]
        fn next(&mut self) -> Option<Self::Item> {
            if self.index >= self.len {
                return None;
            }
            let offset = size_of::<u32>() + (T::get_blitz_size() as usize) * self.index as usize;
            let buffer = unsafe {
                &mut *std::ptr::slice_from_raw_parts_mut(
                    self.buffer.as_mut_ptr().add(offset),
                    T::get_blitz_size() as usize,
                )
            };

            self.index += 1;
            Some(T::new_blitz_builder(
                &self.backend,
                buffer,
                self.self_offset + offset as u32,
            ))
        }
    }

    // endregion: BlitzIterWriter

    // region: BlitzVector

    pub struct BlitzVector<'a, T> {
        buffer: &'a [u8],
        _pd: PhantomData<T>,
    }

    impl<T> BlitzSized for BlitzVector<'_, T> {
        #[inline(always)]
        fn get_blitz_size() -> u32 {
            size_of::<u32>() as u32
        }
    }

    impl<T> BlitzCheck for BlitzVector<'_, T>
    where
        T: BlitzCheck + BlitzSized,
    {
        #[inline(always)]
        fn blitz_check(buffer: &[u8]) -> Result<(), String> {
            if buffer.len() < Self::get_blitz_size() as usize {
                return Err(format!(
                    "Expected buffer to be big enough to contain offset to vector"
                ));
            }

            let offset = unsafe { u32::read_le_bytes(buffer) } as usize;
            let start_of_content = offset + size_of::<u32>();
            if buffer.len() < start_of_content {
                return Err(format!(
                    "Expected buffer to be minimum {} bytes, but it was only {} bytes.",
                    start_of_content,
                    buffer.len()
                ));
            }

            let len = unsafe { u32::read_le_bytes(buffer.get_unchecked(offset..)) } as usize;
            if len == 0 {
                return Ok(());
            }

            let entries_size = len * T::get_blitz_size() as usize;
            if buffer.len() < start_of_content + entries_size {
                return Err(format!(
                    "Expected vector to contain {} entries ({} bytes), but it can only contain {} bytes.",
                    len,
                    entries_size,
                    buffer.len() - start_of_content
                ));
            }

            for index in 0..len {
                let entry_offset = start_of_content + index * T::get_blitz_size() as usize;
                T::blitz_check(unsafe { buffer.get_unchecked(entry_offset..) })
                    .map_err(|err| format!("[index {}] {}", index, err))?;
            }

            Ok(())
        }
    }

    impl<'a, T> BlitzViewer<'a> for BlitzVector<'a, T> {
        #[inline(always)]
        fn new_blitz_view(buffer: &'a [u8]) -> Self {
            Self {
                buffer,
                _pd: PhantomData,
            }
        }
    }

    impl<'a, T> BlitzVector<'a, T> {
        #[inline(always)]
        pub fn offset(&self) -> u32 {
            unsafe { u32::read_le_bytes(self.buffer) }
        }

        #[inline(always)]
        pub fn len(&self) -> u32 {
            let offset = self.offset();
            unsafe {
                u32::read_le_bytes(&*std::ptr::slice_from_raw_parts(
                    self.buffer.as_ptr().add(offset as usize),
                    size_of::<u32>(),
                ))
            }
        }
    }

    impl<'a, T> BlitzVector<'a, T>
    where
        T: BlitzSized + BlitzViewer<'a>,
    {
        #[inline(always)]
        fn get(&self, index: usize) -> T {
            let offset = unsafe { u32::read_le_bytes(self.buffer) };
            let entry_offset = offset as usize + index * (T::get_blitz_size() as usize);
            unsafe {
                T::new_blitz_view(&*std::ptr::slice_from_raw_parts(
                    self.buffer.as_ptr().add(entry_offset),
                    T::get_blitz_size() as usize,
                ))
            }
        }

        #[inline(always)]
        pub fn to_vec(&self) -> Vec<T> {
            let len = self.len() as usize;
            let offset = self.offset() as usize;
            let mut buffer = unsafe { self.buffer.get_unchecked(offset + size_of::<u32>()..) };
            let mut out_vec = vec![];
            out_vec.reserve_exact(len as usize);
            for index in 0..len {
                out_vec.push(T::new_blitz_view(buffer));
                buffer = unsafe { buffer.get_unchecked(T::get_blitz_size() as usize..) };
            }
            out_vec
        }
    }

    impl<'a, T> Index<usize> for BlitzVector<'a, T>
    where
        T: BlitzSized + PrimitiveByteFunctions,
    {
        type Output = T;

        #[inline(always)]
        fn index(&self, index: usize) -> &Self::Output {
            let offset = unsafe { u32::read_le_bytes(self.buffer) };
            let entry_offset = offset as usize + index * (T::get_blitz_size() as usize);
            unsafe {
                &*(std::ptr::slice_from_raw_parts(
                    self.buffer.as_ptr().add(entry_offset),
                    T::get_blitz_size() as usize,
                ) as *const T)
            }
        }
    }

    impl<'a> Index<usize> for BlitzVector<'a, &str> {
        type Output = str;

        #[inline(always)]
        fn index(&self, index: usize) -> &Self::Output {
            let content_offset = unsafe { u32::read_le_bytes(self.buffer) };
            if content_offset == 0 {
                return &"";
            }

            let entry_offset = content_offset as usize + index * (size_of::<u32>() as usize);
            let str_offset = unsafe {
                u32::read_le_bytes(&*std::ptr::slice_from_raw_parts(
                    self.buffer.as_ptr().add(entry_offset),
                    4,
                ))
            } as usize;

            if str_offset == 0 {
                return &"";
            }

            unsafe {
                std::ffi::CStr::from_ptr(
                    self.buffer.as_ptr().add(entry_offset + str_offset) as *const i8
                )
                .to_str()
                .unwrap()
            }
        }
    }

    impl<'a, T> IntoIterator for BlitzVector<'a, T>
    where
        T: BlitzSized + BlitzViewer<'a>,
    {
        type Item = T;
        type IntoIter = BlitzIter<'a, T>;

        #[inline(always)]
        fn into_iter(self) -> Self::IntoIter {
            BlitzIter::from_vector(&self)
        }
    }

    impl<'a, T> PartialEq for BlitzVector<'a, T>
    where
        T: PartialEq + BlitzSized + BlitzViewer<'a>,
    {
        fn eq(&self, other: &Self) -> bool {
            BlitzIter::from_vector(self)
                .zip(BlitzIter::from_vector(other))
                .all(|(a, b)| a == b)
        }
    }

    impl<'a, T> std::fmt::Debug for BlitzVector<'a, T>
    where
        T: std::fmt::Debug + BlitzSized + BlitzViewer<'a>,
    {
        fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            let mut list = f.debug_list();
            BlitzIter::from_vector(self).for_each(|e| {
                list.entry(&e);
            });
            list.finish()
        }
    }

    // endregion: BlitzVector

    // region: BlitzIter

    pub struct BlitzIter<'a, T> {
        buffer: &'a [u8],
        _pd: PhantomData<T>,
    }

    impl<'a, T> BlitzIter<'a, T>
    where
        T: BlitzSized + BlitzViewer<'a>,
    {
        #[inline(always)]
        fn from_vector(vec: &BlitzVector<'a, T>) -> Self {
            let offset = vec.offset();
            let len = vec.len();
            let buffer = unsafe {
                &*std::ptr::slice_from_raw_parts(
                    vec.buffer.as_ptr().add(offset as usize + size_of::<u32>()),
                    (len * T::get_blitz_size()) as usize,
                )
            };
            BlitzIter {
                buffer,
                _pd: PhantomData,
            }
        }
    }

    impl<'a, T> Iterator for BlitzIter<'a, T>
    where
        T: BlitzSized + BlitzViewer<'a>,
    {
        type Item = T;

        #[inline(always)]
        fn next(&mut self) -> Option<Self::Item> {
            if self.buffer.len() == 0 {
                return None;
            }

            let res = Some(T::new_blitz_view(self.buffer));

            self.buffer = unsafe { self.buffer.get_unchecked(T::get_blitz_size() as usize..) };
            res
        }
    }

    impl<'a, T> ExactSizeIterator for BlitzIter<'a, T>
    where
        T: BlitzSized + BlitzViewer<'a>,
    {
        #[inline(always)]
        fn len(&self) -> usize {
            self.buffer.len() / T::get_blitz_size() as usize
        }
    }

    // endregion: BlitzIter
}
