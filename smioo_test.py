from managers import SMIOOManager

def test_smioo_manager():
    smioo_manager = SMIOOManager()
    initialized = smioo_manager.initialize_smioo()
    assert initialized, "SMIOO initialization failed"
    assert smioo_manager.info is not None, "SMIOO info should not be None"
    assert smioo_manager.info.InBitsCount >= 0, "Input bits count should be non-negative"
    assert smioo_manager.info.OutBitsCount >= 0, "Output bits count should be non-negative"

def test_input_output_bits():
    smioo_manager = SMIOOManager()
    smioo_manager.initialize_smioo()
    output_bit = smioo_manager.new_output_bit(bit_number=9)
    assert output_bit is not None, "Failed to create new OutputBit"
    assert hasattr(output_bit, "Number"), "OutputBit should have 'Number' attribute"
    assert output_bit.Number == 1, "OutputBit number should be 1"

if __name__ == "__main__":
    smio = SMIOOManager()
    if smio.initialize_smioo() :
        smio.get_info()
        print(f"Input bits: {smio.info.InBitsCount}")
        print(f"Output bits: {smio.info.OutBitsCount}")