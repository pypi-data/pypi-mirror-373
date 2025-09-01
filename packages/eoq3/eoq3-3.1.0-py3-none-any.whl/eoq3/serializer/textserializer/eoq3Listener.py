# Generated from ../eoq3.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .eoq3Parser import eoq3Parser
else:
    from eoq3Parser import eoq3Parser

# This class defines a complete listener for a parse tree produced by eoq3Parser.
class eoq3Listener(ParseTreeListener):

    # Enter a parse tree produced by eoq3Parser#cmds.
    def enterCmds(self, ctx:eoq3Parser.CmdsContext):
        pass

    # Exit a parse tree produced by eoq3Parser#cmds.
    def exitCmds(self, ctx:eoq3Parser.CmdsContext):
        pass


    # Enter a parse tree produced by eoq3Parser#cmd.
    def enterCmd(self, ctx:eoq3Parser.CmdContext):
        pass

    # Exit a parse tree produced by eoq3Parser#cmd.
    def exitCmd(self, ctx:eoq3Parser.CmdContext):
        pass


    # Enter a parse tree produced by eoq3Parser#cmd_arg.
    def enterCmd_arg(self, ctx:eoq3Parser.Cmd_argContext):
        pass

    # Exit a parse tree produced by eoq3Parser#cmd_arg.
    def exitCmd_arg(self, ctx:eoq3Parser.Cmd_argContext):
        pass


    # Enter a parse tree produced by eoq3Parser#cmd_res_name.
    def enterCmd_res_name(self, ctx:eoq3Parser.Cmd_res_nameContext):
        pass

    # Exit a parse tree produced by eoq3Parser#cmd_res_name.
    def exitCmd_res_name(self, ctx:eoq3Parser.Cmd_res_nameContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val.
    def enterVal(self, ctx:eoq3Parser.ValContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val.
    def exitVal(self, ctx:eoq3Parser.ValContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_prim.
    def enterVal_prim(self, ctx:eoq3Parser.Val_primContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_prim.
    def exitVal_prim(self, ctx:eoq3Parser.Val_primContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_bol.
    def enterVal_bol(self, ctx:eoq3Parser.Val_bolContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_bol.
    def exitVal_bol(self, ctx:eoq3Parser.Val_bolContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_u32.
    def enterVal_u32(self, ctx:eoq3Parser.Val_u32Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_u32.
    def exitVal_u32(self, ctx:eoq3Parser.Val_u32Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_u64.
    def enterVal_u64(self, ctx:eoq3Parser.Val_u64Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_u64.
    def exitVal_u64(self, ctx:eoq3Parser.Val_u64Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_i32.
    def enterVal_i32(self, ctx:eoq3Parser.Val_i32Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_i32.
    def exitVal_i32(self, ctx:eoq3Parser.Val_i32Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_i64.
    def enterVal_i64(self, ctx:eoq3Parser.Val_i64Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_i64.
    def exitVal_i64(self, ctx:eoq3Parser.Val_i64Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_f32.
    def enterVal_f32(self, ctx:eoq3Parser.Val_f32Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_f32.
    def exitVal_f32(self, ctx:eoq3Parser.Val_f32Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_f64.
    def enterVal_f64(self, ctx:eoq3Parser.Val_f64Context):
        pass

    # Exit a parse tree produced by eoq3Parser#val_f64.
    def exitVal_f64(self, ctx:eoq3Parser.Val_f64Context):
        pass


    # Enter a parse tree produced by eoq3Parser#val_str.
    def enterVal_str(self, ctx:eoq3Parser.Val_strContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_str.
    def exitVal_str(self, ctx:eoq3Parser.Val_strContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_str_simple.
    def enterVal_str_simple(self, ctx:eoq3Parser.Val_str_simpleContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_str_simple.
    def exitVal_str_simple(self, ctx:eoq3Parser.Val_str_simpleContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_str_quote.
    def enterVal_str_quote(self, ctx:eoq3Parser.Val_str_quoteContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_str_quote.
    def exitVal_str_quote(self, ctx:eoq3Parser.Val_str_quoteContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_dat.
    def enterVal_dat(self, ctx:eoq3Parser.Val_datContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_dat.
    def exitVal_dat(self, ctx:eoq3Parser.Val_datContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_non.
    def enterVal_non(self, ctx:eoq3Parser.Val_nonContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_non.
    def exitVal_non(self, ctx:eoq3Parser.Val_nonContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_lst.
    def enterVal_lst(self, ctx:eoq3Parser.Val_lstContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_lst.
    def exitVal_lst(self, ctx:eoq3Parser.Val_lstContext):
        pass


    # Enter a parse tree produced by eoq3Parser#val_qry.
    def enterVal_qry(self, ctx:eoq3Parser.Val_qryContext):
        pass

    # Exit a parse tree produced by eoq3Parser#val_qry.
    def exitVal_qry(self, ctx:eoq3Parser.Val_qryContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_seg.
    def enterQry_seg(self, ctx:eoq3Parser.Qry_segContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_seg.
    def exitQry_seg(self, ctx:eoq3Parser.Qry_segContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_sym.
    def enterQry_sym(self, ctx:eoq3Parser.Qry_symContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_sym.
    def exitQry_sym(self, ctx:eoq3Parser.Qry_symContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_sym_short.
    def enterQry_sym_short(self, ctx:eoq3Parser.Qry_sym_shortContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_sym_short.
    def exitQry_sym_short(self, ctx:eoq3Parser.Qry_sym_shortContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_sym_his.
    def enterQry_sym_his(self, ctx:eoq3Parser.Qry_sym_hisContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_sym_his.
    def exitQry_sym_his(self, ctx:eoq3Parser.Qry_sym_hisContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_sym_other.
    def enterQry_sym_other(self, ctx:eoq3Parser.Qry_sym_otherContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_sym_other.
    def exitQry_sym_other(self, ctx:eoq3Parser.Qry_sym_otherContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_sym_full.
    def enterQry_sym_full(self, ctx:eoq3Parser.Qry_sym_fullContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_sym_full.
    def exitQry_sym_full(self, ctx:eoq3Parser.Qry_sym_fullContext):
        pass


    # Enter a parse tree produced by eoq3Parser#qry_arg.
    def enterQry_arg(self, ctx:eoq3Parser.Qry_argContext):
        pass

    # Exit a parse tree produced by eoq3Parser#qry_arg.
    def exitQry_arg(self, ctx:eoq3Parser.Qry_argContext):
        pass



del eoq3Parser