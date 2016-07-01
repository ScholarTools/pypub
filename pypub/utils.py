# -*- coding: utf-8 -*-
"""

Generic code for other code


"""

import inspect


def get_class_list_display_string(input_list):
    if len(input_list) == 0:
        return '[]'
    else:
        class_name = type(input_list[0]).__name__
        return 'len:%s [%s]' % (len(input_list),class_name)


def get_truncated_display_string(input_string,max_length = 50):
    if input_string is None:
        return None 
    elif len(input_string) > max_length:
        return str(input_string[:max_length]) + '...'
    else:
        return input_string


def convert_to_dict(obj):
    obj = obj.__dict__
    for k in obj:
        if isinstance(obj[k], list):
            try:
                obj[k] = [convert_to_dict(x) for x in obj[k]]
            except AttributeError:
                pass
    return obj


def refs_to_list(refs):
    ref_list = []
    for ref in refs:
        ref_list.append(convert_to_dict(ref))
    return ref_list


def find_nth(string, target, n):
    # Returns the index of the nth instance of substring 'target'
    # within string 'string'.
    start = string.find(target)
    while start >= 0 and n > 1:
        start = string.find(target, start+len(target))
        n -= 1
    return start


def findValue(tags, tag_name, label_name=None, label_type=None):
        """
        This is a small helper that is used to pull out values from a tag
        given the value of the tags class or id attribute. See the example.

        Parameters:
        -----------
        tag_name : str
            Tag name or type, such as 'li','span', or 'div'
        label_name : str
            Used for selecting a specific value
        label_type: str
            Used to differentiate between 'class' or 'id' labels
        tags : bs4.element.Tag

        Example:
        --------
        # Our goal is to extract: Can. J. Physiol. Pharmacol.
        # One of the tags is:
        <span class="r_publication">Can. J. Physiol. Pharmacol.</span>

        findValue('span', 'class', 'r_publication')

        """
        if label_name is None or label_type is None:
            temp = tags.find(tag_name)
        else:
            temp = tags.find(tag_name, {'%s' % label_type: label_name})

        if temp is None:
            return None
        else:
            text = temp.text.replace('\\xa0', ' ')
            return text


def assign_props_with_function(obj,d_obj,prop_key_info):
    
    """ 
    Function to assign variables from a dictionary to a class object 

    TODO: Finish documentation    
    
    """    
    present = list()
    missing = list()
    for pk in prop_key_info:
        cur_attr = pk[0]
        cur_key  = pk[1]
        cur_func = pk[2]
        try:
            if cur_func is None:
                setattr(obj,cur_attr,d_obj[cur_key])
            else:
                setattr(obj,cur_attr,cur_func(d_obj[cur_key]))
            present.append(cur_key)
        except KeyError:
            setattr(obj,cur_attr,None)
            missing.append(cur_key)
            
    return ObjectAssignmentSummary(d_obj,present,missing)


class ObjectAssignmentSummary():

    """ 
    Summarizes attributes that were assigned and not-assigned in going
    from a dictionary to an object 
    """

    def __init__(self,d_obj,keys_present,keys_missing):

        """
        Parameters:
        -------------------------
        d_obj: dict
            Input dictionary whose values were moved to the object
        present: list
            List of keys whose values were assigned to the object
        missing: list
            List of keys that were not present in the dictionary
        
        """

        self.keys_present = keys_present
        self.keys_missing = keys_missing
        self.unset_keys   = set(d_obj.keys()) - set(keys_present)
        
    def __repr__(self): 
        return print_object(self)


def print_object(obj):

    """ Goal is to eventually mimic Matlab's default display behavior for objects """

    #TODO - have some way of indicating nested function and not doing fancy
    #print for nested objects ...

    #I'd like to clean this up ... 
    # - align names
    # - truncate long strings   
    # return 'test'    

    MAX_WIDTH = 70

    """
    morphology: [1x1 seg_worm.features.morphology]
       posture: [1x1 seg_worm.features.posture]
    locomotion: [1x1 seg_worm.features.locomotion]
          path: [1x1 seg_worm.features.path]
          info: [1x1 seg_worm.info]
    """

    dict_local = obj.__dict__

    key_names      = [x for x in dict_local]    
    key_lengths    = [len(x) for x in key_names]
    max_key_length = max(key_lengths)
    key_padding    = [max_key_length - x for x in key_lengths]
    
    max_leadin_length = max_key_length + 2
    max_value_length  = MAX_WIDTH - max_leadin_length
 
 
    lead_strings   = [' '*x + y + ': ' for x,y in zip(key_padding,key_names)]    
    
    #TODO: Alphabatize the results ????
    #Could pass in as a option
    #TODO: It might be better to test for built in types
    #   Class::Bio.Entrez.Parser.DictionaryElement
    #   => show actual dictionary, not what is above
    
    
    value_strings = []
    for key in dict_local:
        value = dict_local[key]
        try: #Not sure how to test for classes :/
            class_name  = value.__class__.__name__
            module_name = inspect.getmodule(value).__name__
            temp_str    = 'Class::' + module_name + '.' + class_name
        except:
            temp_str    = repr(value)
            if len(temp_str) > max_value_length:
                #type_str = str(type(value))
                #type_str = type_str[7:-2]
                temp_str = str.format('Type::{}, Len: {}',type(value).__name__,len(value))                
  
        value_strings.append(temp_str)    
    
    final_str = ''
    for cur_lead_str, cur_value in zip(lead_strings,value_strings):
        final_str += (cur_lead_str + cur_value + '\n')


    return final_str
    
    #'<\n%s\n>' % str('\n '.join('%s : %s' % (k, repr(v)) for (k, v) in obj.__dict__.iteritems()))    


class Struct:
    """ 
    Simple class for representing dictionaries as objects.
    
    From:
    http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    
        Example:
        my_dict = ['a':1,'b':2]        
        s = utils.Struct(**my_dict)
        s.a
        s.b
        
        TODO:
        I want to pass in as **my_dict or just my_dict and then do
        the conversion. Passing in ** is awkward

    """
    def __init__(self, **entries): 
        self.__dict__.update(entries)
    def __repr__(self): 
        return print_object(self)