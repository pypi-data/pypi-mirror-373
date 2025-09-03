from __future__ import annotations
from typing import *
from tkinter import *
from tkinter import ttk
from functools import partial


class DynamicTree(ttk.Treeview):

    def __init__(self, master, *_, **kwargs):
        super().__init__(master)
        self.master = master
        self._configuration_memory: dict[str, Any] = dict()

        # ---------------------------------------------------------------
        # configuration and defaults
        # IMPORTANT NOTE:  Every key in __config_specs needs a
        #                  corresponding key in _defaults, or the
        #                  program will crash
        # ---------------------------------------------------------------
        # this is a table of all the additional options available to
        # Dynamic course_ttkTreeView and the methods used to set_default_fonts_and_colours those options

        _status_variable: StringVar = StringVar()
        self.__config_specs: dict[str, Callable[[DynamicTree, Any], None]] = {
            'children': partial(self._save_config_spec, 'children'),
            'on_select': partial(self._save_config_spec, 'on_select'),
            'status_var': partial(self._save_config_spec, 'status_var'),
            'right_click': partial(self._save_config_spec, 'status_var'),
        }

        # this is a table of all the additional options available to
        # Dynamic course_ttkTreeView, and their default values
        self._defaults: dict[str, Callable[[DynamicTree, Any], None]]
        self._defaults = {
            'children': lambda children, selected: None,
            'on_select': lambda selected_obj, selected: None,
            'status_var': _status_variable,
            'right_click': lambda selected_obj, selected: None,
        }

        # set options to defaults
        self._configuration_memory = self._defaults.copy()

        # ---------------------------------------------------------------
        # apply user options
        # ---------------------------------------------------------------
        self.configure(**kwargs)

        # ---------------------------------------------------------------
        # setup bindings
        # ---------------------------------------------------------------
        self.bind('<<TreeviewOpen>>', self.open_branch)

    # =================================================================================================
    # configure, cget, etc
    # =================================================================================================
    def _save_config_spec(self, this_property: str, value: Any):
        self._configuration_memory[this_property] = value

    def cget(self, option: str) -> Any:
        if option in self._configuration_memory:
            return self._configuration_memory[option]
        else:
            return super().cget(option)

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._configuration_memory:
                self._configuration_memory[k](v)
            else:
                super().configure(**{k: v})

    # ====================================================================================
    # run a callback routine
    # ====================================================================================
    def __run_callback(self, which_one, *args):
        callback: callable = self.cget(which_one)
        if callback:
            callback(*args)

    # =================================================================================================
    # sub open_branch -> callback for course_ttkTreeView
    # -> dynamically updates the next level of grandchildren, using
    #    callback routine defined by '-children'
    # =================================================================================================
    def open_branch(self, *_):
        item = self.focus()


'''

# ----------------------------------------------------------------------
# sub openbranch -> callback for course_ttkTreeView
# -> dynamically updates the next level of grandchildren, using
#    callback routine defined by '-children'
# ----------------------------------------------------------------------
sub OpenCmd {
    
    # only continue on if callback is defined
    return unless $self->cget(-children);

    # get a list of children of this branch (should this be leaf instead of child?)
    my @children = $self->infoChildren($path);

    # loop through all the children
    my $i = 0;
    my $sep = $self->cget(-separator);
    foreach my $child (@children) {
        my @grandkids;
        

        # update status variable
        (my $node) = $child =~ /^.*?([^\Q$sep\E]*)$/;
        if (length($child) < 30) {
            $$status_ptr = "Scanning node $child";
        }
        else {
            $$status_ptr = "Scanning node ... ".substr($child,-30);
        }
        $i++;
        $$percent_ptr = ($i/@children)*100;
        $mw->update() if $mw;

        # have grandchildren already been defined?
        next if $self->infoChildren($child);

        # define grandchildren for this child
        ($node) = $child =~ /([^\Q$sep\E]*)$/;
        @grandkids = $self->Callback(-children=>$self,$child);

        # avoid infinite loop
        if ($child =~ /\Q$sep$node$sep\E/) {
            @grandkids = (['<etc>',{-state=>'disabled'}]);
        }


        foreach my $kid (@grandkids) {
            my $newkid;
            my %kidhash;
            $newkid = $kid;
            if (ref $kid eq 'ARRAY') {
                $newkid = $kid->[0];
                if (ref $kid->[1] eq 'HASH') {
                    %kidhash = %{$kid->[1]};
                }
            }
            $self->add ("$child$sep$newkid",-text=>$newkid, %kidhash)
                    unless $self->infoExists("$child$sep$newkid");
            $self->hide('entry', "$child$sep$newkid");
        }


    }

    # done, update status variable and progress bar
    $self->autosetmode;
    $$status_ptr = "Done";
    $$percent_ptr = 0;
}



sub selectionSet {
    my $self = shift;
    my $input = shift;
    return unless $self->infoExists($input);
    $self->SUPER::selectionSet($input);
    $self->Callback(-onSelect=>$self,$input);
}

# ======================================================================
# Expand Tree given a specific node to time_start from
# ======================================================================
{ my $goforit;
  my $treetext;
    sub ExpandTree {
        my $self     = shift;
        my $maxdepth = shift;
        my $keeptext = shift || 0;
        $treetext = '';

        my $selection = $self->selectionGet;
        my $select; $select = (ref $selection) ? $selection->[0] : $selection;
        return unless $select;

        $goforit = 1;
        return recursive_expand($self,$select,$maxdepth,$keeptext);
    }

    sub TreeText {
        return ExpandTree(@_,1);
    }

    sub recursive_expand {
        my $self = shift;
        my $path = shift;
        my $maxdepth = shift || 0;
        my $keeptext = shift || 0;
        my $curdepth = shift || 0;

        if ($self->getmode($path) ne 'none') {
            $self->open($path);
        }

        # bail out if curdepth exceeds max
        return if $maxdepth && $curdepth > $maxdepth;

        # keep text
        if ($keeptext) {
            my $sep = $self->cget(-separator);
            (my $ele = $path) =~ s/.*?([^$sep]*)$/$1/;
            $treetext = $treetext . "\n" . "  "x$curdepth . $ele;
        }

        # procreate
        $curdepth++;
        foreach my $child ($self->infoChildren($path)) {
            recursive_expand ($self,$child,
                              $maxdepth,$keeptext,$curdepth) if $goforit;
        }
        return $treetext;
    }

    sub CancelExpandTree {
        my $self = shift;
        $goforit = 0;
    }
}

# ======================================================================
# Collapse Tree given a specific node to time_start from
# ======================================================================
sub CollapseTree {
    my $self = shift;
    my $selection = $self->selectionGet;
    my $select; $select = (ref $selection) ? $selection->[0] : $selection;
    return unless $select;
    recursive_collapse($self,$select);
}
sub recursive_collapse {
    my $self = shift;
    my $path = shift;
    $self->close($path);
    foreach my $child($self->infoChildren($path)) {
        recursive_collapse($self,$child);
    }
}
1;
'''
