import pytest
import numpy as np
from fractions import Fraction
from klotho.tonos.pitch import Pitch, PitchCollection, EquaveCyclicCollection, AddressedPitchCollection
from klotho.tonos.scales import Scale
from klotho.tonos.chords import Chord


class TestPitch:
    """Test the Pitch class functionality"""
    
    def test_pitch_default_construction(self):
        """Test pitch creation with default values"""
        p = Pitch()
        assert p.pitchclass == 'A'
        assert p.octave == 4
        assert p.cents_offset == 0.0
        assert p.partial == 1
        assert abs(p.freq - 440.0) < 1e-6
    
    def test_pitch_string_construction(self):
        """Test pitch creation from string notation"""
        # Basic pitch class with octave
        p1 = Pitch("C4")
        assert p1.pitchclass == "C"
        assert p1.octave == 4
        assert abs(p1.freq - 261.6256) < 1e-4
        
        # Sharp notation
        p2 = Pitch("F#5")
        assert p2.pitchclass == "F#"
        assert p2.octave == 5
        
        # Flat notation
        p3 = Pitch("Bb3")
        assert p3.pitchclass == "Bb"
        assert p3.octave == 3
        
        # Negative octave
        p4 = Pitch("C-1")
        assert p4.pitchclass == "C"
        assert p4.octave == -1
    
    def test_pitch_from_freq(self):
        """Test pitch creation from frequency"""
        # A4 = 440 Hz
        p1 = Pitch.from_freq(440.0)
        assert p1.pitchclass == "A"
        assert p1.octave == 4
        assert abs(p1.cents_offset) < 1e-6
        
        # C4 ≈ 261.63 Hz
        p2 = Pitch.from_freq(261.6256)
        assert p2.pitchclass == "C"
        assert p2.octave == 4
    
    def test_pitch_comparison(self):
        """Test pitch comparison operators"""
        p1 = Pitch("C4")
        p2 = Pitch("C4")
        p3 = Pitch("D4")
        p4 = Pitch("C5")
        
        # Equality
        assert p1 == p2
        assert p1 != p3
        
        # Ordering
        assert p1 < p3  # C4 < D4
        assert p1 < p4  # C4 < C5
        assert p3 > p1  # D4 > C4
        assert p1 <= p2
        assert p1 >= p2


class TestPitchCollection:
    """Test the PitchCollection base class"""
    
    def test_pitch_collection_defaults(self):
        """Test default construction"""
        pc = PitchCollection()
        expected_defaults = [Fraction(1, 1), Fraction(9, 8), Fraction(5, 4), 
                           Fraction(4, 3), Fraction(3, 2), Fraction(5, 3), Fraction(15, 8)]
        assert pc.degrees == expected_defaults
        assert pc.equave == Fraction(2, 1)
        assert pc.interval_type == Fraction
    
    def test_pitch_collection_custom_degrees(self):
        """Test construction with custom degrees"""
        # Fraction input (ratios)
        pc1 = PitchCollection(["1/1", "5/4", "3/2"], interval_type="ratios")
        assert len(pc1.degrees) == 3
        assert pc1.degrees[0] == Fraction(1, 1)
        assert pc1.degrees[1] == Fraction(5, 4)
        assert pc1.degrees[2] == Fraction(3, 2)
        assert pc1.interval_type == Fraction
        
        # Float input (cents)
        pc2 = PitchCollection([0.0, 386.3, 702.0], interval_type="cents")
        assert pc2.interval_type == float
        assert len(pc2.degrees) == 3
        assert pc2.degrees[0] == 0.0
        assert abs(pc2.degrees[1] - 386.3) < 1e-6
        assert abs(pc2.degrees[2] - 702.0) < 1e-6
        assert pc2.equave == 1200.0
    
    def test_pitch_collection_intervals(self):
        """Test interval calculation between degrees"""
        # Fraction intervals
        pc1 = PitchCollection(["1/1", "5/4", "3/2"], interval_type="ratios")
        intervals = pc1.intervals
        assert len(intervals) == 2
        assert intervals[0] == Fraction(5, 4)  # 5/4 / 1/1
        assert intervals[1] == Fraction(6, 5)  # (3/2) / (5/4)
        
        # Cents intervals
        pc2 = PitchCollection([0.0, 386.3, 702.0], interval_type="cents")
        intervals2 = pc2.intervals
        assert len(intervals2) == 2
        assert abs(intervals2[0] - 386.3) < 1e-6
        assert abs(intervals2[1] - 315.7) < 1e-6
    
    def test_pitch_collection_indexing(self):
        """Test various indexing methods"""
        pc = PitchCollection(["1/1", "5/4", "3/2", "2/1"])
        
        # Basic indexing
        assert pc[0] == Fraction(1, 1)
        assert pc[1] == Fraction(5, 4)
        assert pc[-1] == Fraction(2, 1)
        
        # Slice indexing
        subset = pc[1:3]
        assert isinstance(subset, PitchCollection)
        assert len(subset) == 2
        assert subset[0] == Fraction(5, 4)
        
        # Sequence indexing
        selected = pc[[0, 2]]
        assert isinstance(selected, PitchCollection)
        assert len(selected) == 2
        assert selected[0] == Fraction(1, 1)
        assert selected[1] == Fraction(3, 2)
    
    def test_pitch_collection_root_addressing(self):
        """Test creating addressed pitch collections"""
        pc = PitchCollection(["1/1", "5/4", "3/2"])
        
        # Root with string
        addressed = pc.root("C4")
        assert isinstance(addressed, AddressedPitchCollection)
        assert addressed.reference_pitch.pitchclass == "C"
        assert addressed.reference_pitch.octave == 4


class TestEquaveCyclicCollection:
    """Test the EquaveCyclicCollection class"""
    
    def test_equave_cyclic_defaults(self):
        """Test default construction with sorting and deduplication"""
        ecc = EquaveCyclicCollection()
        # Should be sorted and deduplicated version of defaults
        expected = [Fraction(1, 1), Fraction(9, 8), Fraction(5, 4), 
                   Fraction(4, 3), Fraction(3, 2), Fraction(5, 3), Fraction(15, 8)]
        assert ecc.degrees == expected
        assert ecc.equave == Fraction(2, 1)
    
    def test_equave_cyclic_sorting(self):
        """Test automatic sorting of degrees"""
        ecc = EquaveCyclicCollection(["3/2", "1/1", "5/4"])
        assert ecc.degrees == [Fraction(1, 1), Fraction(5, 4), Fraction(3, 2)]
    
    def test_equave_cyclic_deduplication(self):
        """Test automatic removal of duplicates"""
        ecc = EquaveCyclicCollection(["1/1", "5/4", "5/4", "3/2"])
        assert len(ecc.degrees) == 3
        assert ecc.degrees == [Fraction(1, 1), Fraction(5, 4), Fraction(3, 2)]
    
    def test_equave_cyclic_basic_indexing(self):
        """Test basic indexing without complex equave displacement"""
        ecc = EquaveCyclicCollection(["1/1", "5/4", "3/2"])
        
        # Basic indexing
        assert ecc[0] == Fraction(1, 1)
        assert ecc[1] == Fraction(5, 4)
        assert ecc[2] == Fraction(3, 2)
        
        # Simple next octave
        assert ecc[3] == Fraction(2, 1)  # 1/1 * 2/1
        
        # Simple previous octave
        assert ecc[-1] == Fraction(3, 4)  # 3/2 / 2/1
    
    def test_equave_cyclic_simple_slicing(self):
        """Test basic slice indexing"""
        ecc = EquaveCyclicCollection(["1/1", "5/4", "3/2"])
        
        # Basic slice within bounds
        subset1 = ecc[0:2]
        assert isinstance(subset1, PitchCollection)
        assert len(subset1) == 2
    
    def test_equave_cyclic_cents_mode(self):
        """Test EquaveCyclicCollection with cents"""
        # Basic cents collection
        ecc_cents = EquaveCyclicCollection([0.0, 386.3, 702.0], interval_type="cents")
        assert ecc_cents.interval_type == float
        assert len(ecc_cents.degrees) == 3
        assert ecc_cents.degrees[0] == 0.0
        assert abs(ecc_cents.degrees[1] - 386.3) < 1e-6
        assert ecc_cents.equave == 1200.0
        
        # Test infinite indexing with cents
        assert abs(ecc_cents[3] - 1200.0) < 1e-6  # 0.0 + 1200
        assert abs(ecc_cents[4] - 1586.3) < 1e-6  # 386.3 + 1200
        
        # Test negative indexing with cents
        assert abs(ecc_cents[-1] - (-498.0)) < 1e-6  # 702.0 - 1200
    
    def test_equave_cyclic_cents_deduplication(self):
        """Test deduplication with cents"""
        # Test that values within 1e-6 tolerance are deduplicated
        ecc = EquaveCyclicCollection([0.0, 386.3, 386.300001, 702.0], interval_type="cents")
        assert len(ecc.degrees) == 3  # Should deduplicate the close values


class TestAddressedPitchCollection:
    """Test the AddressedPitchCollection class"""
    
    def test_addressed_basic_functionality(self):
        """Test basic addressed pitch collection operations"""
        pc = PitchCollection(["1/1", "5/4", "3/2"])
        addressed = pc.root("C4")
        
        assert addressed.reference_pitch.pitchclass == "C"
        assert addressed.reference_pitch.octave == 4
        assert len(addressed) == 3
        
        # Check that we get Pitch objects back
        p0 = addressed[0]
        assert isinstance(p0, Pitch)
        assert p0.pitchclass == "C"
        assert p0.octave == 4
    
    def test_addressed_iteration(self):
        """Test iteration over addressed collection"""
        pc = PitchCollection(["1/1", "5/4", "3/2"])
        addressed = pc.root("C4")
        
        pitches = list(addressed)
        assert len(pitches) == 3
        assert all(isinstance(p, Pitch) for p in pitches)
        assert pitches[0].pitchclass == "C"


class TestScale:
    """Test the Scale class"""
    
    def test_scale_defaults(self):
        """Test default major scale construction"""
        scale = Scale()
        expected = [Fraction(1, 1), Fraction(9, 8), Fraction(5, 4), 
                   Fraction(4, 3), Fraction(3, 2), Fraction(5, 3), Fraction(15, 8)]
        assert scale.degrees == expected
        assert scale.equave == Fraction(2, 1)
    
    def test_scale_custom_construction(self):
        """Test construction with custom degrees"""
        # Pentatonic scale (ratios)
        penta = Scale(["1/1", "9/8", "5/4", "3/2", "5/3"], interval_type="ratios")
        assert len(penta.degrees) == 5
        assert penta.degrees[0] == Fraction(1, 1)
        assert penta.degrees[-1] == Fraction(5, 3)
        
        # Chromatic scale (cents) - now works!
        chromatic = Scale([i * 100.0 for i in range(12)], interval_type="cents")
        assert chromatic.interval_type == float
        assert len(chromatic.degrees) == 12
        assert chromatic.degrees[0] == 0.0
        assert chromatic.degrees[1] == 100.0
        assert chromatic.equave == 1200.0
    
    def test_scale_unison_insertion(self):
        """Test that unison is automatically inserted if missing"""
        # Without unison
        scale1 = Scale(["9/8", "5/4", "3/2"])
        assert scale1.degrees[0] == Fraction(1, 1)  # Auto-inserted
        assert len(scale1.degrees) == 4
        
        # With unison already present
        scale2 = Scale(["1/1", "9/8", "5/4"])
        assert scale2.degrees[0] == Fraction(1, 1)
        assert len(scale2.degrees) == 3  # No duplicate
    
    def test_scale_equave_removal(self):
        """Test that equave interval is removed from degrees"""
        # Scale with equave included - it should be removed
        scale = Scale(["1/1", "5/4", "3/2", "2/1"])
        # The 2/1 should be removed because it equals the equave
        assert Fraction(2, 1) not in scale.degrees
        assert len(scale.degrees) == 3
    
    def test_scale_basic_indexing(self):
        """Test basic indexing without complex operations"""
        scale = Scale(["1/1", "9/8", "5/4"])
        
        # Current octave
        assert scale[0] == Fraction(1, 1)
        assert scale[1] == Fraction(9, 8)
        assert scale[2] == Fraction(5, 4)
        
        # Next octave - simple cases
        assert scale[3] == Fraction(2, 1)    # 1/1 * 2/1
    
    def test_scale_mode_generation(self):
        """Test modal generation"""
        major = Scale(["1/1", "9/8", "5/4", "4/3", "3/2", "5/3", "15/8"])
        
        # Mode 0 should be the same scale
        mode0 = major.mode(0)
        assert mode0.degrees == major.degrees
        
        # Mode 1 (Dorian)
        dorian = major.mode(1)
        assert isinstance(dorian, Scale)
        assert dorian.degrees[0] == Fraction(1, 1)  # Always starts with unison
        assert len(dorian.degrees) == len(major.degrees)
    
    def test_scale_addressed_creation(self):
        """Test creating addressed scales"""
        scale = Scale(["1/1", "9/8", "5/4"])
        
        # Create addressed scale
        c_major = scale.root("C4")
        assert hasattr(c_major, '_collection')
        
        # Test indexing returns Pitch objects
        c4 = c_major[0]
        assert isinstance(c4, Pitch)
        assert c4.pitchclass == "C"
        assert c4.octave == 4


class TestChord:
    """Test the Chord class"""
    
    def test_chord_defaults(self):
        """Test default major triad construction"""
        chord = Chord()
        expected = [Fraction(1, 1), Fraction(5, 4), Fraction(3, 2)]
        assert chord.degrees == expected
        assert chord.equave == Fraction(2, 1)
    
    def test_chord_custom_construction(self):
        """Test construction with custom degrees"""
        # Minor triad (ratios)
        minor = Chord(["1/1", "6/5", "3/2"], interval_type="ratios")
        assert len(minor.degrees) == 3
        assert minor.degrees[1] == Fraction(6, 5)
        
        # Seventh chord (ratios)
        dom7 = Chord(["1/1", "5/4", "3/2", "7/4"], interval_type="ratios")
        assert len(dom7.degrees) == 4
        assert dom7.degrees[-1] == Fraction(7, 4)
        
        # Cents-based chord - now works!
        cents_chord = Chord([0.0, 386.3, 702.0, 968.8], interval_type="cents")
        assert cents_chord.interval_type == float
        assert len(cents_chord.degrees) == 4
        assert cents_chord.degrees[0] == 0.0
        assert abs(cents_chord.degrees[1] - 386.3) < 1e-6
        assert cents_chord.equave == 1200.0
    
    def test_chord_equave_behavior(self):
        """Test that chords handle equave like scales (remove it)"""
        # Chord with equave included - it should be removed like in Scale
        chord = Chord(["1/1", "5/4", "3/2", "2/1"])
        # The 2/1 should be removed because it equals the equave
        assert Fraction(2, 1) not in chord.degrees
        assert len(chord.degrees) == 3
    
    def test_chord_basic_indexing(self):
        """Test basic indexing"""
        chord = Chord(["1/1", "5/4", "3/2"])
        
        # Basic indexing
        assert chord[0] == Fraction(1, 1)
        assert chord[1] == Fraction(5, 4)
        assert chord[2] == Fraction(3, 2)
        
        # Next octave
        assert chord[3] == Fraction(2, 1)    # 1/1 * 2/1
    
    def test_chord_inversion_operations(self):
        """Test chord inversion methods"""
        chord = Chord(["1/1", "5/4", "3/2"])
        
        # Test invert operator
        inverted = ~chord
        assert isinstance(inverted, Chord)
        assert len(inverted.degrees) == len(chord.degrees)
        
        # Test negative operator (should be same as invert)
        negated = -chord
        assert negated.degrees == inverted.degrees
    
    def test_chord_addressed_creation(self):
        """Test creating addressed chords"""
        chord = Chord(["1/1", "5/4", "3/2"])
        
        # Create addressed chord
        c_major = chord.root("C4")
        assert hasattr(c_major, '_collection')
        
        # Test indexing returns Pitch objects
        c4 = c_major[0]
        assert isinstance(c4, Pitch)
        assert c4.pitchclass == "C"
        assert c4.octave == 4


class TestBasicIntegration:
    """Test basic integration between classes"""
    
    def test_pitch_collection_set_operations_fractions(self):
        """Test set operations with fraction collections only"""
        pc1 = PitchCollection(["1/1", "5/4", "3/2"])
        pc2 = PitchCollection(["1/1", "4/3", "3/2"])
        
        # Union
        union = pc1 | pc2
        assert len(union) == 4  # 1/1, 5/4, 4/3, 3/2
        assert Fraction(1, 1) in union.degrees
        assert Fraction(5, 4) in union.degrees
        assert Fraction(4, 3) in union.degrees
        assert Fraction(3, 2) in union.degrees
        
        # Intersection
        intersection = pc1 & pc2
        assert len(intersection) == 2  # 1/1, 3/2
        assert Fraction(1, 1) in intersection.degrees
        assert Fraction(3, 2) in intersection.degrees
    
    def test_real_world_musical_scenarios(self):
        """Test realistic musical scenarios"""
        # Major scale in C
        c_major_scale = Scale().root("C4")
        c4 = c_major_scale[0]  # C4
        d4 = c_major_scale[1]  # D4
        e4 = c_major_scale[2]  # E4
        
        assert c4.pitchclass == "C"
        assert d4.pitchclass == "D"
        assert e4.pitchclass == "E"
        
        # Major triad in different keys
        major_triad = Chord()
        
        # C major
        c_maj = major_triad.root("C4")
        assert c_maj[0].pitchclass == "C"
        
        # F# major
        fs_maj = major_triad.root("F#3")
        assert fs_maj[0].pitchclass == "F#"
        assert fs_maj[0].octave == 3
    
    def test_caching_behavior(self):
        """Test that addressed creation uses caching"""
        chord = Chord(["1/1", "5/4", "3/2"])
        scale = Scale(["1/1", "9/8", "5/4"])
        root_pitch = Pitch("C4")
        
        # Test that multiple calls to root() return cached objects
        addressed_chord1 = chord.root(root_pitch)
        addressed_chord2 = chord.root(root_pitch)
        assert addressed_chord1 is addressed_chord2
        
        addressed_scale1 = scale.root(root_pitch)
        addressed_scale2 = scale.root(root_pitch)
        assert addressed_scale1 is addressed_scale2


class TestCentsAndMixedOperations:
    """Test cents-based operations and mixed type operations"""
    
    def test_cents_scales_now_work(self):
        """FIXED: Cents-based scales now work with explicit interval_type"""
        # These now work with explicit interval_type
        scale1 = Scale([0.0, 100.0, 200.0], interval_type="cents")
        assert len(scale1.degrees) == 3
        assert scale1.interval_type == float
        assert scale1.equave == 1200.0
        
        chromatic = Scale([i * 100.0 for i in range(12)], interval_type="cents")
        assert len(chromatic.degrees) == 12
        assert chromatic.interval_type == float
        
        # Test addressing with cents scale
        c_chromatic = chromatic.root("C4")
        assert isinstance(c_chromatic[0], Pitch)
    
    def test_cents_chords_now_work(self):
        """FIXED: Cents-based chords now work with explicit interval_type"""
        chord1 = Chord([0.0, 400.0, 700.0], interval_type="cents")
        assert len(chord1.degrees) == 3
        assert chord1.interval_type == float
        assert chord1.equave == 1200.0
        
        # Test addressing with cents chord
        c_major_cents = chord1.root("C4")
        assert isinstance(c_major_cents[0], Pitch)
    
    def test_mixed_type_operations_work(self):
        """Test operations between different interval types"""
        fraction_pc = PitchCollection(["1/1", "5/4", "3/2"], interval_type="ratios")
        float_pc = PitchCollection([0.0, 386.3, 702.0], interval_type="cents")
        
        # Union should work by converting types
        union = fraction_pc | float_pc
        assert isinstance(union, PitchCollection)
        
        # Other operations should also work
        intersection = fraction_pc & float_pc
        assert isinstance(intersection, PitchCollection)
    
    def test_from_intervals_with_interval_type(self):
        """Test from_intervals with explicit interval_type"""
        # From ratio intervals
        pc1 = PitchCollection.from_intervals(["9/8", "10/9"], interval_type="ratios")
        assert pc1.interval_type == Fraction
        assert len(pc1) == 3  # Should include starting 1/1
        
        # From cents intervals
        pc2 = PitchCollection.from_intervals([203.9, 182.4], interval_type="cents")
        assert pc2.interval_type == float
        assert len(pc2) == 3
        assert pc2.degrees[0] == 0.0
