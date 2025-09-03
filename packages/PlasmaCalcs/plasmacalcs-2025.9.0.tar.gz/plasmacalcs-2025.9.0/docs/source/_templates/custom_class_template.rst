{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :inherited-members:

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::

   {# special methods #}
   {% for m in methods %}
     {% if m.startswith('__') and m.endswith('__') %}
       ~{{ name }}.{{ m }}
     {% endif %}
   {%- endfor %}

   {# normal methods #}
   {% for m in methods %}
     {% if not m.startswith('_') %}
       ~{{ name }}.{{ m }}
     {% endif %}
   {%- endfor %}

   {# private methods #}
   {% for m in methods %}
     {% if m.startswith('_') and not (m.startswith('__') and m.endswith('__')) %}
       ~{{ name }}.{{ m }}
     {% endif %}
   {%- endfor %}

   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
