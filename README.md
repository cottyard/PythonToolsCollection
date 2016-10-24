TTTT is a python-based tool for text generation that transforms xml files to plain text.

# I. Hello World

Your xml file should have `<ttt>` as its root tag. There are a bunch of different tags, each having its own transformation rule, e.g., `<raw>` is a tag that does no transformation:
```
<ttt>
    <raw>content</raw>
</ttt>
```

>content

`<br>` transforms to a line break:
```
<ttt>
    <raw>hello,<br/>world</raw>
</ttt>
```
>hello,<br/>
>world

# II. Environment

During the transformation, there is a python environment that you can interact with through tags.

You can load variables into the environment from python source files using `<loadenv>`, and define new tags with environment variables using `<define> `.

Let's say we have a source file env.py:
```
content = 'apple'
```
Then these tags
```
<ttt>
   <loadenv src='env.py'/>
   <define tag='fruit'>content</define>
   <raw>An <fruit/> a day keeps the doctor away.</raw>
</ttt>
```
will transform to

>An apple a day keeps the doctor away.

In the content of `<define>` you can write python expressions that evaluate to strings. In the example the tag `<fruit>` is created, and it transforms to the value of the environment variable `content`. Note that `<fruit>`'s life scope is the parent tag of the `<define>` tag that created it.

You may also write python statements to change the environment using `<execute>`.
```
<ttt>
   <loadenv src='env.py'/>
   <define tag='fruit'>content</define>
   <execute>content = 'onion'</execute> 
   <raw>An <fruit/> a day keeps the doctor away.</raw>
</ttt>
```
>An onion a day keeps the doctor away.

Like tags created by `<define>`, `<execute>`'s life scope is restricted to its parent tag, so the change to the environment variable is effective only inside `<ttt>`.

# III. Text Generating

env.py:
```
fruit = 'cherry'
```
```
<ttt>
   <loadenv src='env.py'/>
   <select cond="fruit">
      <case cond="'cherry'"><raw>More, please.</raw></case>
      <case cond="'cantaloupe'"><raw>I'm full.</raw></case>
      <default><raw>No, thanks.</raw></default>
   </select>
</ttt>
```
>More, please.

`<select>` and `<case>` have a `cond` attribute that takes an expression. `<select>` searches the `<case>` tags for a `cond` expression match, and stops at the first success, or at the `<default>` tag.

The following example shows how `<repeat>` works:
```
<ttt>
   <raw>Why is the ocean blue? 'Cause all the fish go "</raw>
   <repeat times="6">
      <raw>blue </raw>
   </repeat>
   <raw>blue".</raw>
</ttt>
```

>Why is the ocean blue? 'Cause all the fish go "blue blue blue blue blue blue blue".

Now you can list variables in the environment like this:

env.py:
```
fruit_list = ['apple', 'banana', 'cantaloupe']
```
```
<ttt>
   <loadenv src='env.py'/>
   <execute>iterator = iter(fruit_list)</execute>
   <define tag='fruit'>fruit</define>
   <repeat times='len(fruit_list)'>
      <execute>fruit = iterator.next()</execute>
      <fruit/><br/>
   </repeat>
</ttt>
```
>apple<br/>
>banana<br/>
>cantaloupe

In fact, you can escape from the boilerplate using `<enumerate>`:

env.py:
```
fruit_list = ['apple', 'banana', 'cantaloupe']
```
```
<ttt>
   <loadenv src='env.py'/>
   <enumerate container='fruit_list' item='fruit'>
      <raw><index/> <fruit/><br/></raw>
   </enumerate>
</ttt>
```
>0 apple<br/>
>1 banana<br/>
>2 cantaloupe<br/>

TTTT will not gain its full power until the advent of `<transform>`:

fruit.xml:
```
<ttt>
   <raw>durian</raw>
</ttt> 
```
```
<ttt>
   <raw>help yourselves to some </raw>
   <transform template="fruit.xml" environment="{}"/>
</ttt>
```
>help yourselves to some durian

The `template` attribute specifies the path to *fruit.xml*, while `environment` specifies a dictionary serving as the environment for *fruit.xml*.

# IV. Attribute Collecting

Tags can collect missing attributes from child tags. This enables dynamically generated tag attributes.

Road_66.xml:
```
<ttt>
   <raw>It's high noon somewhere in the world.</raw>
</ttt>
```
env.py:
```
place = 'Road_66'
```
file.txt.xml:
```
<ttt>
   <loadenv src='env.py'/>
   <define tag="where">place + '.xml'</define>
   <transform environment="{}">
      <template><where/></template>
   </transform>
</ttt>
```
>It's high noon somewhere in the world.

The `template` attribute of `<transform>` is generated and collected.
